import 'dart:async';
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:roadwatch_mobile/core/errors/app_exception.dart';
import 'package:roadwatch_mobile/core/services/image_source_service.dart';
import 'package:roadwatch_mobile/core/services/location_service.dart';
import 'package:roadwatch_mobile/features/report/domain/report_models.dart';
import 'package:roadwatch_mobile/providers.dart';

/// Everything about the report currently being created.
/// `null` for analysis/submission means "not started yet".
class ReportDraftState {
  final File? image;
  final bool pickFailed;
  final bool locating;
  final LocationResult? location;
  final AsyncValue<AnalysisResult>? analysis;
  final String notes;
  final AsyncValue<SubmittedReport>? submission;

  const ReportDraftState({
    this.image,
    this.pickFailed = false,
    this.locating = false,
    this.location,
    this.analysis,
    this.notes = '',
    this.submission,
  });

  bool get hasLocation => location is LocationFound;

  /// A photo, a position and a finished analysis are required. Zero
  /// detections still allows submitting ("submit anyway", M-7). A failed
  /// analysis does not. Blocks double submission.
  bool get canSubmit {
    final sub = submission;
    final alreadySubmittingOrDone = sub != null && !sub.hasError;
    return image != null &&
        hasLocation &&
        (analysis?.hasValue ?? false) &&
        !alreadySubmittingOrDone;
  }

  ReportDraftState copyWith({
    File? image,
    bool? pickFailed,
    bool? locating,
    LocationResult? location,
    AsyncValue<AnalysisResult>? analysis,
    String? notes,
    AsyncValue<SubmittedReport>? submission,
  }) {
    return ReportDraftState(
      image: image ?? this.image,
      pickFailed: pickFailed ?? this.pickFailed,
      locating: locating ?? this.locating,
      location: location ?? this.location,
      analysis: analysis ?? this.analysis,
      notes: notes ?? this.notes,
      submission: submission ?? this.submission,
    );
  }
}

class ReportDraftController extends Notifier<ReportDraftState> {
  @override
  ReportDraftState build() => const ReportDraftState();

  AppException _asAppException(Object e) =>
      e is AppException ? e : UnknownException(e.toString());

  /// Picks a photo, then fetches the location and the AI analysis in parallel.
  /// Picks a photo and starts the location and AI analysis in the background.
  /// Returns true if a photo was chosen, so the caller can navigate right away.
  Future<bool> pickPhoto(PhotoSource source) async {
    if (state.pickFailed) state = state.copyWith(pickFailed: false);

    final File? file;
    try {
      file = await ref.read(imageSourceServiceProvider).pick(source);
    } on ImagePickException {
      state = state.copyWith(pickFailed: true);
      return false;
    }
    if (file == null) return false; // user cancelled

    // New photo: start a fresh draft, keeping the typed notes and last location.
    state = ReportDraftState(
      image: file,
      notes: state.notes,
      location: state.location,
    );

    unawaited(Future.wait([analyze(), refreshLocation()]));
    return true;
  }

  Future<void> refreshLocation() async {
    if (state.locating) return;
    state = state.copyWith(locating: true);
    final result = await ref.read(locationServiceProvider).getCurrentLocation();
    state = state.copyWith(locating: false, location: result);
  }

  Future<void> analyze() async {
    final image = state.image;
    if (image == null) return;

    state = state.copyWith(analysis: const AsyncValue.loading());
    try {
      final result = await ref.read(reportRepositoryProvider).analyze(image);
      if (state.image != image) return; // the photo changed meanwhile
      state = state.copyWith(analysis: AsyncValue.data(result));
    } catch (e, st) {
      if (state.image != image) return;
      state = state.copyWith(
        analysis: AsyncValue.error(_asAppException(e), st),
      );
    }
  }

  void setNotes(String value) => state = state.copyWith(notes: value);

  Future<void> submit() async {
    final current = state;
    final location = current.location;
    if (!current.canSubmit || location is! LocationFound) return;

    state = current.copyWith(submission: const AsyncValue.loading());
    try {
      final notes = current.notes.trim();
      final result = await ref
          .read(reportRepositoryProvider)
          .submit(
            ReportSubmission(
              image: current.image!,
              latitude: location.coordinates.latitude,
              longitude: location.coordinates.longitude,
              notes: notes.isEmpty ? null : notes,
            ),
          );
      state = state.copyWith(submission: AsyncValue.data(result));
    } catch (e, st) {
      state = state.copyWith(
        submission: AsyncValue.error(_asAppException(e), st),
      );
    }
  }

  /// Call after the confirmation screen to start a new report.
  void reset() => state = const ReportDraftState();
}

final reportDraftProvider =
    NotifierProvider<ReportDraftController, ReportDraftState>(
      ReportDraftController.new,
    );

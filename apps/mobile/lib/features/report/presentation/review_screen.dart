import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/router.dart';
import 'package:roadwatch_mobile/app/theme.dart';
import 'package:roadwatch_mobile/core/errors/error_messages.dart';
import 'package:roadwatch_mobile/core/services/image_source_service.dart';
import 'package:roadwatch_mobile/core/services/location_service.dart';
import 'package:roadwatch_mobile/core/widgets/ai_disclaimer_banner.dart';
import 'package:roadwatch_mobile/features/report/presentation/report_draft_controller.dart';
import 'package:roadwatch_mobile/features/report/presentation/widgets/severity_chip.dart';
import 'package:roadwatch_mobile/providers.dart';

class ReviewScreen extends ConsumerWidget {
  const ReviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final draft = ref.watch(reportDraftProvider);
    final controller = ref.read(reportDraftProvider.notifier);

    ref.listen(reportDraftProvider.select((s) => s.submission), (_, next) {
      if (next == null) return;
      if (next.hasValue) {
        context.go(AppRoutes.confirmation);
      } else if (next.hasError) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(errorMessage(next.error!))));
      }
    });

    final submitting = draft.submission?.isLoading ?? false;

    return Scaffold(
      appBar: AppBar(title: const Text('Review report')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            if (draft.image != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(
                  draft.image!,
                  height: 240,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
            const SizedBox(height: 16),
            _AnalysisSection(draft: draft, controller: controller),
            const SizedBox(height: 16),
            _LocationTile(draft: draft, controller: controller, ref: ref),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: draft.notes,
              onChanged: controller.setNotes,
              maxLines: 3,
              // TODO: add a maxLength once Member 2 confirms the notes limit.
              decoration: const InputDecoration(labelText: 'Notes (optional)'),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: draft.canSubmit ? controller.submit : null,
              child: submitting
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Submit report'),
            ),
            if (!draft.canSubmit && draft.submission == null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  !draft.hasLocation
                      ? 'A location is required to submit.'
                      : 'Waiting for the AI analysis.',
                  textAlign: TextAlign.center,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _AnalysisSection extends StatelessWidget {
  final ReportDraftState draft;
  final ReportDraftController controller;

  const _AnalysisSection({required this.draft, required this.controller});

  @override
  Widget build(BuildContext context) {
    final analysis = draft.analysis;

    if (analysis == null || analysis.isLoading) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              SizedBox(
                height: 24,
                width: 24,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              SizedBox(width: 16),
              Expanded(
                child: Text(
                  'Analyzing your photo… the first request can take a while '
                  'if the server is waking up.',
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (analysis.hasError) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(errorMessage(analysis.error!)),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                children: [
                  FilledButton(
                    onPressed: controller.analyze,
                    child: const Text('Try again'),
                  ),
                  OutlinedButton(
                    onPressed: () => controller.pickPhoto(PhotoSource.gallery),
                    child: const Text('Choose another photo'),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }

    final result = analysis.requireValue;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (result.hasDetections) ...[
              Text(
                'Detected damage',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              for (final d in result.detections)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Row(
                    children: [
                      Expanded(child: Text(d.category)),
                      Text(
                        '${(d.confidence * 100).round()}%',
                        style: AppText.data,
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 8),
              SeverityChip(severity: result.severity),
            ] else ...[
              Text(
                'No road damage detected',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 4),
              const Text(
                'You can retake the photo, or submit the report anyway.',
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: () => controller.pickPhoto(PhotoSource.camera),
                icon: const Icon(Icons.photo_camera),
                label: const Text('Retake photo'),
              ),
            ],
            const SizedBox(height: 12),
            const AiDisclaimerBanner(),
          ],
        ),
      ),
    );
  }
}

class _LocationTile extends StatelessWidget {
  final ReportDraftState draft;
  final ReportDraftController controller;
  final WidgetRef ref;

  const _LocationTile({
    required this.draft,
    required this.controller,
    required this.ref,
  });

  @override
  Widget build(BuildContext context) {
    final location = draft.location;
    final service = ref.read(locationServiceProvider);

    if (draft.locating || location == null) {
      return const Card(
        child: ListTile(
          leading: SizedBox(
            height: 24,
            width: 24,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          title: Text('Getting your location…'),
        ),
      );
    }

    final (icon, title, actions) = switch (location) {
      LocationFound(:final coordinates) => (
        Icons.location_on,
        '${coordinates.latitude.toStringAsFixed(5)}, '
            '${coordinates.longitude.toStringAsFixed(5)}',
        <Widget>[],
      ),
      LocationServiceDisabled() => (
        Icons.location_off,
        'Location is turned off',
        <Widget>[
          TextButton(
            onPressed: service.openLocationSettings,
            child: const Text('Turn on'),
          ),
          TextButton(
            onPressed: controller.refreshLocation,
            child: const Text('Try again'),
          ),
        ],
      ),
      LocationPermissionDenied() => (
        Icons.location_disabled,
        'Location permission is needed to send your report',
        <Widget>[
          TextButton(
            onPressed: controller.refreshLocation,
            child: const Text('Allow'),
          ),
        ],
      ),
      LocationPermissionBlocked() => (
        Icons.location_disabled,
        'Location permission is blocked',
        <Widget>[
          TextButton(
            onPressed: service.openAppSettings,
            child: const Text('Open settings'),
          ),
          TextButton(
            onPressed: controller.refreshLocation,
            child: const Text('Try again'),
          ),
        ],
      ),
      LocationUnavailable() => (
        Icons.location_searching,
        'Could not get your location',
        <Widget>[
          TextButton(
            onPressed: controller.refreshLocation,
            child: const Text('Try again'),
          ),
        ],
      ),
    };

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    title,
                    style: location is LocationFound ? AppText.data : null,
                  ),
                ),
              ],
            ),
            if (actions.isNotEmpty) Wrap(spacing: 8, children: actions),
          ],
        ),
      ),
    );
  }
}

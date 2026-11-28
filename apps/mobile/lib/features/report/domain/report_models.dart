import 'dart:io';

/// Preliminary severity of the detected damage. `none` is the zero-detection case.
enum Severity { none, low, medium, high }

/// One damage detection returned by the AI.
class Detection {
  /// Human-readable damage category. The final naming (class codes vs labels)
  /// is still to be agreed with Member 2 / the ML team.
  final String category;

  /// Confidence from 0.0 to 1.0.
  final double confidence;

  const Detection({required this.category, required this.confidence});
}

/// Result of analyzing a photo (shown before the user submits).
class AnalysisResult {
  final List<Detection> detections;
  final Severity severity;

  const AnalysisResult({required this.detections, required this.severity});

  /// False means the zero-detection case: offer "retake" or "submit anyway".
  bool get hasDetections => detections.isNotEmpty;
}

/// Everything the user is submitting.
class ReportSubmission {
  final File image;
  final double latitude;
  final double longitude;
  final String? notes;

  const ReportSubmission({
    required this.image,
    required this.latitude,
    required this.longitude,
    this.notes,
  });
}

/// Confirmation returned after a successful submit.
class SubmittedReport {
  final String reportId;

  /// Final severity, if the backend returns one (open question for Member 2).
  final Severity? severity;

  const SubmittedReport({required this.reportId, this.severity});
}

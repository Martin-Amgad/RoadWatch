import 'dart:io';

import 'package:roadwatch_mobile/features/report/domain/report_models.dart';

/// The only thing screens and controllers know about the backend.
/// Implementations: MockReportRepository now, ApiReportRepository once the
/// API contract is agreed. Both throw AppException subclasses on failure.
abstract class ReportRepository {
  /// Sends the photo for AI analysis and returns the preview result.
  Future<AnalysisResult> analyze(File image);

  /// Submits the complete report and returns the confirmation.
  Future<SubmittedReport> submit(ReportSubmission submission);
}

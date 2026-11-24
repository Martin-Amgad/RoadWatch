import 'dart:io';

import 'package:roadwatch_mobile/core/errors/app_exception.dart';
import 'package:roadwatch_mobile/features/report/domain/report_models.dart';
import 'package:roadwatch_mobile/features/report/domain/report_repository.dart';

/// What the mock should simulate. Change [MockReportRepository.scenario]
/// to exercise every UI state (M-7) without a backend.
enum MockScenario {
  success,
  noDetections,
  timeout,
  noConnection,
  badImage,
  serverError,
}

class MockReportRepository implements ReportRepository {
  final MockScenario scenario;
  final Duration delay;

  const MockReportRepository({
    this.scenario = MockScenario.success,
    this.delay = const Duration(milliseconds: 1500),
  });

  @override
  Future<AnalysisResult> analyze(File image) async {
    await Future<void>.delayed(delay);

    switch (scenario) {
      case MockScenario.timeout:
        throw const RequestTimeoutException();
      case MockScenario.noConnection:
        throw const NoConnectionException();
      case MockScenario.badImage:
        throw const InvalidImageException();
      case MockScenario.serverError:
        throw const ServerException(statusCode: 500);
      case MockScenario.noDetections:
        return const AnalysisResult(detections: [], severity: Severity.none);
      case MockScenario.success:
        return const AnalysisResult(
          detections: [
            Detection(category: 'Longitudinal crack', confidence: 0.91),
            Detection(category: 'Pothole', confidence: 0.78),
          ],
          severity: Severity.high,
        );
    }
  }

  @override
  Future<SubmittedReport> submit(ReportSubmission submission) async {
    await Future<void>.delayed(delay);

    switch (scenario) {
      case MockScenario.timeout:
        throw const RequestTimeoutException();
      case MockScenario.noConnection:
        throw const NoConnectionException();
      case MockScenario.badImage:
        throw const InvalidImageException();
      case MockScenario.serverError:
        throw const ServerException(statusCode: 500);
      case MockScenario.noDetections:
        return const SubmittedReport(
          reportId: 'MOCK-0002',
          severity: Severity.none,
        );
      case MockScenario.success:
        return const SubmittedReport(
          reportId: 'MOCK-0001',
          severity: Severity.high,
        );
    }
  }
}

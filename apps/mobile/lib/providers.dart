import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:roadwatch_mobile/app/config.dart';
import 'package:roadwatch_mobile/core/network/dio_client.dart';
import 'package:roadwatch_mobile/core/services/geolocator_location_service.dart';
import 'package:roadwatch_mobile/core/services/image_picker_service.dart';
import 'package:roadwatch_mobile/core/services/image_source_service.dart';
import 'package:roadwatch_mobile/core/services/location_service.dart';
import 'package:roadwatch_mobile/features/report/data/mock_report_repository.dart';
import 'package:roadwatch_mobile/features/report/domain/report_repository.dart';

/// The shared HTTP client. Built once from AppConfig and reused everywhere.
final dioProvider = Provider<Dio>((ref) => createDio());

/// The single switch between mock and real backend.
final reportRepositoryProvider = Provider<ReportRepository>((ref) {
  if (AppConfig.useMock) {
    // Change the scenario here to test each UI state.
    return const MockReportRepository(scenario: MockScenario.success);
  }

  // TODO: return ApiReportRepository(ref.watch(dioProvider)) once the
  // endpoint paths and field names are confirmed by Member 2.
  throw UnimplementedError('Real repository pending the API contract');
});

/// Real GPS by default. To test the UI states, temporarily return
/// const MockLocationService(scenario: ...) from mock_location_service.dart.
final locationServiceProvider = Provider<LocationService>(
  (ref) => const GeolocatorLocationService(),
);

final imageSourceServiceProvider = Provider<ImageSourceService>(
  (ref) => ImagePickerService(),
);

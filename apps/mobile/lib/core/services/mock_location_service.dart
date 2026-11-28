import 'package:roadwatch_mobile/core/services/location_service.dart';

enum MockLocationScenario {
  found,
  serviceDisabled,
  denied,
  blocked,
  unavailable,
}

/// For testing every location UI state without touching device settings.
class MockLocationService implements LocationService {
  final MockLocationScenario scenario;

  const MockLocationService({this.scenario = MockLocationScenario.found});

  @override
  Future<LocationResult> getCurrentLocation() async {
    await Future<void>.delayed(const Duration(milliseconds: 500));

    return switch (scenario) {
      MockLocationScenario.found => const LocationFound(
        Coordinates(latitude: 30.0444, longitude: 31.2357),
      ),
      MockLocationScenario.serviceDisabled => const LocationServiceDisabled(),
      MockLocationScenario.denied => const LocationPermissionDenied(),
      MockLocationScenario.blocked => const LocationPermissionBlocked(),
      MockLocationScenario.unavailable => const LocationUnavailable(),
    };
  }

  @override
  Future<void> openAppSettings() async {}

  @override
  Future<void> openLocationSettings() async {}
}

/// A GPS position. Plain Dart, no package types leak out of the service.
class Coordinates {
  final double latitude;
  final double longitude;

  const Coordinates({required this.latitude, required this.longitude});
}

/// Every outcome of asking for the location (M-3). Sealed, so the UI's
/// switch must handle each case.
sealed class LocationResult {
  const LocationResult();
}

class LocationFound extends LocationResult {
  final Coordinates coordinates;
  const LocationFound(this.coordinates);
}

/// GPS is switched off on the device. UI: offer openLocationSettings().
class LocationServiceDisabled extends LocationResult {
  const LocationServiceDisabled();
}

/// Permission denied, but the user can still be asked again.
class LocationPermissionDenied extends LocationResult {
  const LocationPermissionDenied();
}

/// Permission denied permanently. UI: offer openAppSettings().
class LocationPermissionBlocked extends LocationResult {
  const LocationPermissionBlocked();
}

/// Permission is fine but no fix was obtained (timeout or platform error).
class LocationUnavailable extends LocationResult {
  const LocationUnavailable();
}

abstract class LocationService {
  /// Checks GPS and permission (asking if needed), then returns a position.
  /// Never throws: every failure is a [LocationResult].
  Future<LocationResult> getCurrentLocation();

  Future<void> openAppSettings();
  Future<void> openLocationSettings();
}

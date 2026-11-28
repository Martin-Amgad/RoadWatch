import 'package:geolocator/geolocator.dart';
import 'package:roadwatch_mobile/core/services/location_service.dart';

class GeolocatorLocationService implements LocationService {
  const GeolocatorLocationService();

  @override
  Future<LocationResult> getCurrentLocation() async {
    try {
      if (!await Geolocator.isLocationServiceEnabled()) {
        return const LocationServiceDisabled();
      }

      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      switch (permission) {
        case LocationPermission.denied:
          return const LocationPermissionDenied();
        case LocationPermission.deniedForever:
          return const LocationPermissionBlocked();
        case LocationPermission.unableToDetermine:
          return const LocationUnavailable();
        case LocationPermission.whileInUse || LocationPermission.always:
          break;
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 15),
        ),
      );

      return LocationFound(
        Coordinates(latitude: position.latitude, longitude: position.longitude),
      );
    } catch (_) {
      // Timeout or platform error: the UI treats it as "no fix, try again".
      return const LocationUnavailable();
    }
  }

  @override
  Future<void> openAppSettings() => Geolocator.openAppSettings();

  @override
  Future<void> openLocationSettings() => Geolocator.openLocationSettings();
}

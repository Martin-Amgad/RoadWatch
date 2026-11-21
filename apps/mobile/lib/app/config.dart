/// Central place for settings that differ between environments.
///
/// Override at launch with --dart-define, for example:
///   flutter run --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=https://my-api.onrender.com
/// A full restart is needed after changing these (hot reload does not re-read them).
class AppConfig {
  AppConfig._();

  /// Base URL of the backend API, including scheme and host, but not path.
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );
  static const String apiVersionPath = String.fromEnvironment(
    'API_VERSION_PATH',
    defaultValue: '/api/v1',
  );
  static const String apiUrl = '$apiBaseUrl$apiVersionPath';

  /// Defaults to true while the backend is not ready. Final release build must
  /// be made with --dart-define=USE_MOCK=false (add to the Week 3 checklist).
  static const bool useMock = bool.fromEnvironment(
    'USE_MOCK',
    defaultValue: true,
  );

  /// Covers a Render free-tier cold start, when the container may be waking up.
  static const Duration connectTimeout = Duration(seconds: 35);

  /// Longest wait: must cover synchronous YOLO inference plus any remaining
  /// wake-up time. Revisit after the Week 2 latency benchmark.
  static const Duration receiveTimeout = Duration(seconds: 65);

  /// Photo upload over possibly weak mobile data.
  static const Duration sendTimeout = Duration(seconds: 35);
}

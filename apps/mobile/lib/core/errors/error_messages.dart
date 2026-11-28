import 'package:roadwatch_mobile/core/errors/app_exception.dart';

/// User-facing text for each failure (M-7). Exhaustive over AppException.
String errorMessage(Object error) {
  if (error is! AppException) return 'Something went wrong. Please try again.';

  return switch (error) {
    NoConnectionException() =>
      'No internet connection. Check your connection and try again.',
    RequestTimeoutException() => 'The server took too long to respond. If it was idle it may need up to a minute to wake up, so please try again.',
    InvalidImageException() =>
      'This photo could not be processed. Please take or choose another one.',
    ServerException() =>
      'The server had a problem. Please try again in a moment.',
    UnknownException() => 'Something went wrong. Please try again.',
  };
}

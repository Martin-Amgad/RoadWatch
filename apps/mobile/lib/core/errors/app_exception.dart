/// Base type for every failure the UI needs to distinguish.
///
/// Sealed: all subclasses live in this file, so a `switch` over an
/// [AppException] is exhaustive. Adding a new subclass makes every
/// switch that misses it a compile error, instead of a runtime surprise.
///
/// [message] is for logs and debugging only. The user-facing text is
/// chosen by the UI layer.
sealed class AppException implements Exception {
  final String message;
  const AppException(this.message);

  @override
  String toString() => '$runtimeType: $message';
}

/// The device has no network connection at all.
class NoConnectionException extends AppException {
  const NoConnectionException() : super('No network connection');
}

/// Connect, send or receive timeout (M-7). Not named TimeoutException,
/// to avoid clashing with the one in dart:async.
class RequestTimeoutException extends AppException {
  const RequestTimeoutException() : super('The request timed out');
}

/// The server rejected the image: corrupt, unsupported type or too large (M-7).
class InvalidImageException extends AppException {
  /// Whatever explanation the server sent, if any. The error body format
  /// is not yet agreed with the backend, so this stays a plain string.
  final String? serverMessage;

  const InvalidImageException({this.serverMessage})
    : super('The image was rejected by the server');
}

/// A 5xx or any other unexpected HTTP response.
class ServerException extends AppException {
  final int? statusCode;

  const ServerException({this.statusCode})
    : super('Unexpected server response');
}

/// Anything not classified above, so nothing escapes as a raw crash.
class UnknownException extends AppException {
  const UnknownException([super.message = 'Unknown error']);
}

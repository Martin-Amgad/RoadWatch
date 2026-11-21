sealed class AppException implements Exception {
  final String message;
  const AppException(this.message);
}

/// The device is not connected to the internet.
class NoConnectionException extends AppException {
  const NoConnectionException()
    : super('No internet connection. Please check your network settings.');
}

/// The request took too long to complete. This can happen if the server is slow or the network is weak.
class RequestTimeoutException extends AppException {
  const RequestTimeoutException()
    : super('The request timed out. Please try again later.');
}

/// The server rejected the image: corrupt, unsupported type or too large (M-7).
class InvalidImageException extends AppException {
  /// Whatever explanation the server sent, if any. The error body format
  /// is not yet agreed with the backend, so this stays a plain string.
  final String? serverMessage;

  const InvalidImageException({this.serverMessage})
    : super('The image was rejected by the server');
}

// The server returned a non-200 status code, which is not expected for a successful request.
class ServerException extends AppException {
  final int statusCode;
  const ServerException(this.statusCode)
    : super('Server error occurred. Status code: $statusCode');
}

/// An unexpected error occurred, which is not covered by the other exception types.
/// This is a catch-all for unanticipated issues.
class UnknownException extends AppException {
  const UnknownException() : super('An unknown error occurred.');
}

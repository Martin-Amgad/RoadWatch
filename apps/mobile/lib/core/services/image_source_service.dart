import 'dart:io';

enum PhotoSource { camera, gallery }

/// The picker failed (for example the camera app is unavailable).
/// Cancelling is NOT a failure: pick() returns null for that.
class ImagePickException implements Exception {
  final String message;
  const ImagePickException(this.message);

  @override
  String toString() => 'ImagePickException: $message';
}

abstract class ImageSourceService {
  /// Returns the chosen photo, or null if the user cancelled.
  Future<File?> pick(PhotoSource source);
}

import 'dart:io';

import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:roadwatch_mobile/core/services/image_source_service.dart';

class ImagePickerService implements ImageSourceService {
  final ImagePicker _picker;

  ImagePickerService([ImagePicker? picker]) : _picker = picker ?? ImagePicker();

  // TODO(confirm with Member 2): upload size limits and accepted formats.
  // Until then, downscale so photos are small enough to upload quickly.
  static const double _maxDimension = 1280;
  static const int _quality = 85;

  @override
  Future<File?> pick(PhotoSource source) async {
    try {
      final picked = await _picker.pickImage(
        source: source == PhotoSource.camera
            ? ImageSource.camera
            : ImageSource.gallery,
        maxWidth: _maxDimension,
        maxHeight: _maxDimension,
        imageQuality: _quality,
      );
      return picked == null ? null : File(picked.path);
    } on PlatformException catch (e) {
      throw ImagePickException(e.message ?? e.code);
    }
  }
}

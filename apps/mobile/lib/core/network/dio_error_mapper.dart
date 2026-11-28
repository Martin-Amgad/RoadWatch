import 'package:dio/dio.dart';
import 'package:roadwatch_mobile/core/errors/app_exception.dart';

const _imageRejectedStatuses = {400, 413, 415, 422};

AppException mapDioException(DioException e) {
  // Avoid mapping an exception that's already mapped.
  if (e.error is AppException) {
    return e.error as AppException;
  }

  return switch (e.type) {
    DioExceptionType.connectionTimeout ||
    DioExceptionType.sendTimeout ||
    DioExceptionType.receiveTimeout => RequestTimeoutException(),

    DioExceptionType.connectionError => NoConnectionException(),

    DioExceptionType.badResponse => _mapBadResponse(e),

    DioExceptionType.badCertificate => UnknownException(),

    DioExceptionType.cancel => UnknownException(),

    DioExceptionType.unknown => UnknownException(),

    DioExceptionType.transformTimeout => UnknownException(),
  };
}

AppException _mapBadResponse(DioException e) {
  final statusCode = e.response?.statusCode;

  // Replace this condition with the image-related status codes
  // or response indicators defined by your API.
  if (_imageRejectedStatuses.contains(statusCode)) {
    return const InvalidImageException();
  }
  return ServerException(statusCode: statusCode ?? 0);
}

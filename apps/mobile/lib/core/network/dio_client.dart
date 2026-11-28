import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:roadwatch_mobile/app/config.dart';

Dio createDio() {
  final options = BaseOptions(
    baseUrl: AppConfig.apiUrl,
    connectTimeout: AppConfig.connectTimeout,
    receiveTimeout: AppConfig.receiveTimeout,
    sendTimeout: AppConfig.sendTimeout,
    headers: {'Accept': 'application/json'},
  );
  final dio = Dio(options);
  if (kDebugMode) {
    dio.interceptors.add(
      LogInterceptor(requestBody: false, responseBody: false),
    );
  }
  return dio;
}

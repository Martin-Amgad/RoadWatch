import 'package:flutter/services.dart';
import 'package:material_ui/material_ui.dart';

/// Design tokens from DESIGN.md ("Civic Infrastructure Assurance").
class AppColors {
  AppColors._();

  static const primary = Color(0xFF1B4332);
  static const primaryActive = Color(0xFF143326);
  static const secondary = Color(0xFF2D6A4F);
  static const accent = Color(0xFF40916C);
  static const focusRing = Color(0xFF52B788);

  static const ink = Color(0xFF1A202C);
  static const inkMuted = Color(0xFF475569);
  static const placeholder = Color(0xFF94A3B8);

  static const border = Color(0xFFE2E8F0);
  static const borderStrong = Color(0xFFCBD5E1);
  static const background = Color(0xFFF8FAFC);
  static const recessed = Color(0xFFF1F5F9);
  static const surface = Color(0xFFFFFFFF);

  static const high = Color(0xFFDC2626);
  static const highBg = Color(0xFFFEF2F2);
  static const medium = Color(0xFFD97706);
  static const mediumBg = Color(0xFFFFFBEB);
  static const low = Color(0xFF059669);
  static const lowBg = Color(0xFFECFDF5);

  static const inverseSurface = Color(0xFF2A303D);

  static const secondaryContainer = Color(0xFFAEEECB);
  static const onSecondaryContainer = Color(0xFF316E52);
  static const primaryFixed = Color(0xFFC1ECD4);
  static const primaryFixedDim = Color(0xFFA5D0B9);
  static const surfaceContainerLow = Color(0xFFF1F3FF);
  static const surfaceContainerHigh = Color(0xFFE3E8F9);
  static const errorContainer = Color(0xFFFFDAD6);
  static const onErrorContainer = Color(0xFF93000A);
}

class AppText {
  AppText._();

  /// GPS coordinates, report IDs, confidence values: tabular figures and
  /// slashed zeros so numbers align (DESIGN.md typography).
  static const data = TextStyle(
    fontFamily: 'Inter',
    fontSize: 13,
    height: 18 / 13,
    fontWeight: FontWeight.w500,
    color: AppColors.ink,
    fontFeatures: [FontFeature.tabularFigures(), FontFeature.slashedZero()],
  );
}

TextStyle _ts(
  String family,
  double size,
  FontWeight weight,
  double lineHeight, [
  double spacingEm = 0,
]) {
  return TextStyle(
    fontFamily: family,
    fontSize: size,
    fontWeight: weight,
    height: lineHeight / size,
    letterSpacing: size * spacingEm,
    color: AppColors.ink,
  );
}

TextTheme _textTheme() {
  const head = 'PlusJakartaSans';
  const body = 'Inter';
  return TextTheme(
    headlineMedium: _ts(
      head,
      30,
      FontWeight.w700,
      38,
      -0.015,
    ), // headline-xl-mobile
    headlineSmall: _ts(
      head,
      24,
      FontWeight.w700,
      32,
      -0.01,
    ), // headline-lg-mobile
    titleLarge: _ts(head, 22, FontWeight.w600, 28, -0.01), // headline-md
    titleMedium: _ts(head, 18, FontWeight.w600, 24, -0.005), // headline-sm
    titleSmall: _ts(body, 14, FontWeight.w600, 20, 0.01), // label-lg
    bodyLarge: _ts(body, 16, FontWeight.w400, 24),
    bodyMedium: _ts(body, 14, FontWeight.w400, 20),
    bodySmall: _ts(body, 12, FontWeight.w400, 16),
    labelLarge: _ts(body, 14, FontWeight.w600, 20, 0.01),
    labelMedium: _ts(body, 12, FontWeight.w600, 16, 0.02),
    labelSmall: _ts(body, 11, FontWeight.w600, 14, 0.04),
  );
}

ThemeData buildAppTheme() {
  const scheme = ColorScheme.light(
    primary: AppColors.primary,
    onPrimary: Colors.white,
    secondary: AppColors.secondary,
    onSecondary: Colors.white,
    surface: AppColors.surface,
    onSurface: AppColors.ink,
    error: AppColors.high,
    onError: Colors.white,
    outline: AppColors.borderStrong,
    outlineVariant: AppColors.border,
  );

  final text = _textTheme();
  final buttonShape = RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(8),
  );
  const buttonSize = Size(64, 44); // 44px touch target

  OutlineInputBorder inputBorder(Color color, [double width = 1]) =>
      OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: color, width: width),
      );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    fontFamily: 'Inter',
    textTheme: text,
    scaffoldBackgroundColor: AppColors.background,
    dividerColor: AppColors.border,
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.background,
      foregroundColor: AppColors.ink,
      elevation: 0,
      scrolledUnderElevation: 0,
      surfaceTintColor: Colors.transparent,
      centerTitle: false,
      titleTextStyle: text.titleMedium,
      systemOverlayStyle: SystemUiOverlayStyle.dark,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: ButtonStyle(
        minimumSize: const WidgetStatePropertyAll(buttonSize),
        shape: WidgetStatePropertyAll(buttonShape),
        textStyle: WidgetStatePropertyAll(text.labelLarge),
        elevation: const WidgetStatePropertyAll(0),
        backgroundColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.disabled)) return AppColors.border;
          if (states.contains(WidgetState.pressed)) {
            return AppColors.primaryActive;
          }
          if (states.contains(WidgetState.hovered)) return AppColors.secondary;
          return AppColors.primary;
        }),
        foregroundColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.disabled)
              ? AppColors.inkMuted
              : Colors.white,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: ButtonStyle(
        minimumSize: const WidgetStatePropertyAll(buttonSize),
        shape: WidgetStatePropertyAll(buttonShape),
        textStyle: WidgetStatePropertyAll(text.labelLarge),
        backgroundColor: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.pressed)
              ? AppColors.background
              : AppColors.surface,
        ),
        foregroundColor: const WidgetStatePropertyAll(AppColors.ink),
        side: WidgetStateProperty.resolveWith(
          (states) => BorderSide(
            color:
                states.contains(WidgetState.pressed) ||
                    states.contains(WidgetState.hovered)
                ? AppColors.borderStrong
                : AppColors.border,
          ),
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: ButtonStyle(
        minimumSize: const WidgetStatePropertyAll(Size(64, 40)),
        shape: WidgetStatePropertyAll(buttonShape),
        textStyle: WidgetStatePropertyAll(text.labelLarge),
        foregroundColor: const WidgetStatePropertyAll(AppColors.secondary),
      ),
    ),
    cardTheme: CardThemeData(
      color: AppColors.surface,
      elevation: 0,
      margin: EdgeInsets.zero,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: AppColors.border),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surface,
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      hintStyle: text.bodyMedium!.copyWith(color: AppColors.placeholder),
      labelStyle: text.bodyMedium!.copyWith(color: AppColors.inkMuted),
      border: inputBorder(AppColors.borderStrong),
      enabledBorder: inputBorder(AppColors.borderStrong),
      focusedBorder: inputBorder(AppColors.secondary, 2),
      errorBorder: inputBorder(AppColors.high),
      focusedErrorBorder: inputBorder(AppColors.high, 2),
    ),
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: AppColors.secondary,
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.inverseSurface,
      contentTextStyle: text.bodyMedium!.copyWith(color: Colors.white),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
  );
}

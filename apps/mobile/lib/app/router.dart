import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:roadwatch_mobile/core/storage/preferences.dart';
import 'package:roadwatch_mobile/features/onboarding/privacy_screen.dart';
import 'package:roadwatch_mobile/features/report/presentation/confirmation_screen.dart';
import 'package:roadwatch_mobile/features/report/presentation/home_screen.dart';
import 'package:roadwatch_mobile/features/report/presentation/report_draft_controller.dart';
import 'package:roadwatch_mobile/features/report/presentation/review_screen.dart';

class AppRoutes {
  AppRoutes._();

  static const privacy = '/privacy';
  static const home = '/';
  static const review = '/review';
  static const confirmation = '/confirmation';
}

final routerProvider = Provider<GoRouter>((ref) {
  final prefs = ref.read(sharedPreferencesProvider);

  return GoRouter(
    initialLocation: AppRoutes.home,
    redirect: (context, state) {
      final accepted = prefs.getBool(privacyAcceptedKey) ?? false;
      final at = state.matchedLocation;

      // First launch: privacy notice before anything else.
      if (!accepted) return at == AppRoutes.privacy ? null : AppRoutes.privacy;
      if (at == AppRoutes.privacy) return AppRoutes.home;

      // Guards: no review without a photo, no confirmation without a result.
      final draft = ref.read(reportDraftProvider);
      if (at == AppRoutes.review && draft.image == null) return AppRoutes.home;
      if (at == AppRoutes.confirmation &&
          !(draft.submission?.hasValue ?? false)) {
        return AppRoutes.home;
      }
      return null;
    },
    routes: [
      GoRoute(
        path: AppRoutes.privacy,
        builder: (context, state) => const PrivacyScreen(),
      ),
      GoRoute(
        path: AppRoutes.home,
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: AppRoutes.review,
        builder: (context, state) => const ReviewScreen(),
      ),
      GoRoute(
        path: AppRoutes.confirmation,
        builder: (context, state) => const ConfirmationScreen(),
      ),
    ],
  );
});

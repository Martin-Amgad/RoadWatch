import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/router.dart';
import 'package:roadwatch_mobile/core/storage/preferences.dart';

/// Shown once, on first launch (Privacy NFR).
class PrivacyScreen extends ConsumerWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Privacy notice')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Expanded(
                child: SingleChildScrollView(
                  child: Text(
                    'RoadWatch helps you report road damage to your municipality.\n\n'
                    'When you submit a report, the app sends:\n'
                    '  •  the photo you take or choose\n'
                    '  •  your current GPS location\n'
                    '  •  the optional notes you write\n\n'
                    'Photos may accidentally show people or vehicle license '
                    'plates. Please frame your photo on the road surface and '
                    'avoid capturing faces or plates where you can.\n\n'
                    'An AI model analyzes your photo and gives a preliminary '
                    'estimate only. Municipal staff review every report and '
                    'make all repair decisions.',
                    style: TextStyle(fontSize: 16, height: 1.4),
                  ),
                ),
              ),
              SizedBox(
                width: double.infinity,
                child: FilledButton(
                  onPressed: () async {
                    await ref
                        .read(sharedPreferencesProvider)
                        .setBool(privacyAcceptedKey, true);
                    if (context.mounted) context.go(AppRoutes.home);
                  },
                  child: const Text('I understand'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

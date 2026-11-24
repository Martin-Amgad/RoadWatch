import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/router.dart';
import 'package:roadwatch_mobile/core/services/image_source_service.dart';
import 'package:roadwatch_mobile/features/report/presentation/report_draft_controller.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  Future<void> _pick(
    BuildContext context,
    WidgetRef ref,
    PhotoSource source,
  ) async {
    final controller = ref.read(reportDraftProvider.notifier);
    final chosen = await controller.pickPhoto(source);
    if (!context.mounted) return;

    if (chosen) {
      context.push(AppRoutes.review);
    } else if (ref.read(reportDraftProvider).pickFailed) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not open the camera or gallery.')),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('RoadWatch')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              Icon(Icons.add_road, size: 72, color: scheme.primary),
              const SizedBox(height: 16),
              Text(
                'Report road damage',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              const Text(
                'Take a photo of the damage. We will check it with AI, '
                'attach your location, and send it to the municipality.',
                textAlign: TextAlign.center,
              ),
              const Spacer(),
              FilledButton.icon(
                onPressed: () => _pick(context, ref, PhotoSource.camera),
                icon: const Icon(Icons.photo_camera),
                label: const Text('Take a photo'),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => _pick(context, ref, PhotoSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('Choose from gallery'),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

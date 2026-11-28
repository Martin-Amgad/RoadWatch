import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/config.dart';
import 'package:roadwatch_mobile/app/router.dart';
import 'package:roadwatch_mobile/app/theme.dart';
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
    final text = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 64,
        titleSpacing: 16,
        title: Row(
          children: [
            const _LogoMark(),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.account_balance_outlined,
                        size: 14,
                        color: AppColors.secondary,
                      ),
                      const SizedBox(width: 4),
                      Flexible(
                        child: Text(
                          AppConfig.authorityName.toUpperCase(),
                          overflow: TextOverflow.ellipsis,
                          style: text.labelSmall!.copyWith(
                            color: AppColors.secondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                  Text('RoadWatch', style: text.titleMedium),
                ],
              ),
            ),
          ],
        ),
      ),
      body: SafeArea(
        top: false,
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
          child: Column(
            spacing: 16,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const _Greeting(),
              _HeroCard(
                onCamera: () => _pick(context, ref, PhotoSource.camera),
                onGallery: () => _pick(context, ref, PhotoSource.gallery),
              ),
              const _HowItWorks(),
              const _GuaranteeCard(),
              const _HazardNotice(),
            ],
          ),
        ),
      ),
    );
  }
}

/// Placeholder mark. To use the real logo, export it to
/// assets/images/logo.png, declare it in pubspec.yaml, and swap the Icon
/// for Image.asset('assets/images/logo.png').
class _LogoMark extends StatelessWidget {
  const _LogoMark();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: AppColors.primary,
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Icon(Icons.add_road, size: 18, color: Colors.white),
    );
  }
}

class _Greeting extends StatelessWidget {
  const _Greeting();

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(
              Icons.verified_outlined,
              size: 16,
              color: AppColors.secondary,
            ),
            const SizedBox(width: 4),
            Text(
              'CITIZEN REPORTING',
              style: text.labelSmall!.copyWith(color: AppColors.secondary),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text('Welcome', style: text.headlineSmall),
        const SizedBox(height: 4),
        Row(
          children: [
            const Icon(Icons.domain, size: 18, color: AppColors.secondary),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                AppConfig.authorityName,
                style: text.bodyMedium!.copyWith(color: AppColors.inkMuted),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _HeroCard extends StatelessWidget {
  final VoidCallback onCamera;
  final VoidCallback onGallery;

  const _HeroCard({required this.onCamera, required this.onGallery});

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: Container(
        color: AppColors.primary,
        padding: const EdgeInsets.all(24),
        child: Stack(
          children: [
            Positioned(
              right: -32,
              top: -32,
              child: Container(
                width: 144,
                height: 144,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.secondaryContainer.withValues(alpha: 0.10),
                ),
              ),
            ),
            SizedBox(
              width: double.infinity,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(9999),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.bolt,
                          size: 14,
                          color: AppColors.primaryFixed,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'AI Assisted · Staff Reviewed',
                          style: text.labelSmall!.copyWith(
                            color: AppColors.primaryFixed,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Report a Problem',
                    style: text.titleLarge!.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Snap a photo. Our AI suggests what the issue is and how '
                    'urgent it looks, then your report goes to the municipal team.',
                    style: text.bodyMedium!.copyWith(
                      color: AppColors.primaryFixedDim,
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: onCamera,
                      icon: const Icon(Icons.photo_camera, size: 20),
                      label: const Text('Start New Report'),
                      style: FilledButton.styleFrom(
                        backgroundColor: AppColors.secondaryContainer,
                        foregroundColor: AppColors.onSecondaryContainer,
                      ),
                    ),
                  ),
                  Center(
                    child: TextButton.icon(
                      onPressed: onGallery,
                      icon: const Icon(Icons.photo_library_outlined, size: 18),
                      label: const Text('Or choose a photo from your gallery'),
                      style: TextButton.styleFrom(
                        foregroundColor: AppColors.primaryFixed,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HowItWorks extends StatelessWidget {
  const _HowItWorks();

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'How It Works',
              style: text.titleMedium!.copyWith(fontWeight: FontWeight.w700),
            ),
            Row(
              children: [
                const Icon(
                  Icons.format_list_numbered,
                  size: 14,
                  color: AppColors.secondary,
                ),
                const SizedBox(width: 2),
                Text(
                  '3-Step Process',
                  style: text.labelSmall!.copyWith(color: AppColors.secondary),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Card(
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              children: [
                _Step(
                  number: 1,
                  title: 'Capture the Issue',
                  body: 'Take a clear photo of the problem from a safe spot.',
                  icon: Icons.add_a_photo_outlined,
                ),
                _StepConnector(),
                _Step(
                  number: 2,
                  title: 'AI Pre-Screening',
                  body:
                      'Computer vision suggests what the issue is and a '
                      'preliminary severity rating.',
                  icon: Icons.psychology_outlined,
                  highlighted: true,
                ),
                _StepConnector(),
                _Step(
                  number: 3,
                  title: 'Municipal Review',
                  body:
                      'City staff review your report, prioritize it and '
                      'arrange the work.',
                  icon: Icons.local_shipping_outlined,
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _Step extends StatelessWidget {
  final int number;
  final String title;
  final String body;
  final IconData icon;
  final bool highlighted;

  const _Step({
    required this.number,
    required this.title,
    required this.body,
    required this.icon,
    this.highlighted = false,
  });

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 32,
          height: 32,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: highlighted
                ? AppColors.secondaryContainer
                : AppColors.surfaceContainerHigh,
          ),
          child: Text(
            '$number',
            style: text.labelMedium!.copyWith(
              fontWeight: FontWeight.w700,
              color: highlighted
                  ? AppColors.onSecondaryContainer
                  : AppColors.primary,
            ),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    title,
                    style: text.labelLarge!.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Icon(
                    icon,
                    size: 15,
                    color: highlighted
                        ? AppColors.secondary
                        : AppColors.inkMuted,
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Text(
                body,
                style: text.bodySmall!.copyWith(color: AppColors.inkMuted),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _StepConnector extends StatelessWidget {
  const _StepConnector();

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.only(left: 15, top: 4, bottom: 4),
        child: Container(
          width: 2,
          height: 12,
          color: AppColors.surfaceContainerHigh,
        ),
      ),
    );
  }
}

class _GuaranteeCard extends StatelessWidget {
  const _GuaranteeCard();

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surfaceContainerLow,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.verified_user_outlined,
                size: 16,
                color: AppColors.secondary,
              ),
              const SizedBox(width: 8),
              Text(
                'Responsible AI Guarantee',
                style: text.labelMedium!.copyWith(color: AppColors.secondary),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Automated classifications are preliminary estimates that help '
            'staff prioritize. Every report is reviewed by municipal staff, '
            'who make all final decisions.',
            style: text.bodySmall!.copyWith(
              color: AppColors.inkMuted,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _HazardNotice extends StatelessWidget {
  const _HazardNotice();

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.errorContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.warning_amber_rounded, color: AppColors.high),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Immediate Hazard Notice',
                  style: text.labelLarge!.copyWith(
                    fontWeight: FontWeight.w700,
                    color: AppColors.onErrorContainer,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'For immediate dangers such as blocked traffic lanes, gas '
                  'leaks or sinkholes, contact your local emergency services '
                  'directly instead of using this app.',
                  style: text.bodySmall!.copyWith(
                    color: AppColors.onErrorContainer,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

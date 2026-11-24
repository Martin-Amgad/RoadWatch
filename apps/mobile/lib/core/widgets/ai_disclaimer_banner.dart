import 'package:flutter/widgets.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/theme.dart';

/// Responsible AI Assurance Panel (M-9). Show wherever AI output appears.
class AiDisclaimerBanner extends StatelessWidget {
  const AiDisclaimerBanner({super.key});

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(7),
        child: IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(width: 3, color: AppColors.secondary),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(12),
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
                          const SizedBox(width: 6),
                          Text(
                            'AI analysis · preliminary',
                            style: text.labelMedium,
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'AI detections and severity ratings are preliminary '
                        'estimates to help staff prioritize. They are not '
                        'engineering measurements, and municipal staff make all '
                        'repair decisions.',
                        style: text.bodySmall!.copyWith(
                          color: AppColors.inkMuted,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

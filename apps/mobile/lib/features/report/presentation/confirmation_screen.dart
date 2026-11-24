import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/router.dart';
import 'package:roadwatch_mobile/core/widgets/ai_disclaimer_banner.dart';
import 'package:roadwatch_mobile/features/report/presentation/report_draft_controller.dart';
import 'package:roadwatch_mobile/features/report/presentation/widgets/severity_chip.dart';

class ConfirmationScreen extends ConsumerWidget {
  const ConfirmationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final report = ref.watch(reportDraftProvider).submission?.value;
    if (report == null) return const SizedBox.shrink();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Report submitted'),
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              Icon(
                Icons.check_circle,
                size: 80,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: 16),
              Text(
                'Thank you!',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              const Text('Your report ID', textAlign: TextAlign.center),
              SelectableText(
                report.reportId,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              if (report.severity != null) ...[
                const SizedBox(height: 12),
                Center(child: SeverityChip(severity: report.severity!)),
              ],
              const SizedBox(height: 24),
              const AiDisclaimerBanner(),
              const Spacer(),
              FilledButton(
                onPressed: () {
                  context.go(AppRoutes.home);
                  ref.read(reportDraftProvider.notifier).reset();
                },
                child: const Text('Report another problem'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

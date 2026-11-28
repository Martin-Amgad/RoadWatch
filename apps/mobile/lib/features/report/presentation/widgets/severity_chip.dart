import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/theme.dart';
import 'package:roadwatch_mobile/features/report/domain/report_models.dart';

/// Severity badge (DESIGN.md "Civic Status & Severity Badges").
/// Always labeled preliminary, since severity is an AI estimate.
class SeverityChip extends StatelessWidget {
  final Severity severity;
  const SeverityChip({super.key, required this.severity});

  @override
  Widget build(BuildContext context) {
    final (label, fg, bg) = switch (severity) {
      Severity.none => ('None', AppColors.inkMuted, AppColors.recessed),
      Severity.low => ('Low', AppColors.low, AppColors.lowBg),
      Severity.medium => ('Medium', AppColors.medium, AppColors.mediumBg),
      Severity.high => ('High', AppColors.high, AppColors.highBg),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(9999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: fg, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text(
            '$label · preliminary',
            style: Theme.of(context).textTheme.labelSmall!.copyWith(color: fg),
          ),
        ],
      ),
    );
  }
}

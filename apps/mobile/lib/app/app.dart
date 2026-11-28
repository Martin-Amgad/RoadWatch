import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';
import 'package:roadwatch_mobile/app/router.dart';
import 'package:roadwatch_mobile/app/theme.dart';

class RoadWatchApp extends ConsumerWidget {
  const RoadWatchApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'RoadWatch',
      theme: buildAppTheme(),
      routerConfig: ref.watch(routerProvider),
    );
  }
}

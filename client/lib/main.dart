import 'package:flutter/material.dart';
import 'config/app_router.dart';

void main() {
  runApp(const TangkapinApp());
}

class TangkapinApp extends StatelessWidget {
  const TangkapinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Tangkapin',
      debugShowCheckedModeBanner: false,
      routerConfig: AppRouter.router,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFE3F553),
          brightness: Brightness.light,
        ),
        fontFamily: 'Inter',
      ),
    );
  }
}
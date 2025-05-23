import 'package:go_router/go_router.dart';
import '../screens/splash_screen.dart';
import '../screens/login_screen.dart';
import '../screens/register_screen.dart';
import '../screens/main_screen.dart';
import '../screens/report_details_screen.dart';
import '../screens/camera_detail_screen.dart';
import '../screens/police_tracking_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/main',
        name: 'main',
        builder: (context, state) => const MainScreen(),
      ),
      GoRoute(
        path: '/report/:id',
        name: 'report_details',
        builder: (context, state) {
          final reportId = state.pathParameters['id'] ?? '1';
          return ReportDetailsScreen(reportId: reportId);
        },
      ),
      GoRoute(
        path: '/camera/:id',
        name: 'camera_details',
        builder: (context, state) {
          final cameraId = state.pathParameters['id'] ?? 'CH01';
          return CameraDetailScreen(cameraId: cameraId);
        },
      ),
      GoRoute(
        path: '/police-tracking/:id',
        name: 'police_tracking',
        builder: (context, state) {
          final reportId = state.pathParameters['id'] ?? '1';
          return PoliceTrackingScreen(reportId: reportId);
        },
      ),
    ],
  );
}
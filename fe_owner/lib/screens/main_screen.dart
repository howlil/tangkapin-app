import 'package:flutter/material.dart';
import '../layouts/main_layout.dart';
import 'home_screen.dart';
import 'cameras_screen.dart';
import 'reports_screen.dart';
import 'profile_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const CamerasScreen(),
    const ReportsScreen(),
    const ProfileScreen(),
  ];

  final List<String> _titles = [
    'Dashboard',
    'Cameras',
    'Reports',
    'Profile',
  ];

  void _onBottomBarTap(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Don't show appbar title for profile screen
    final bool showTitle = _currentIndex != 3;
    
    return MainLayout(
      title: showTitle ? _titles[_currentIndex] : '',
      showBackButton: false,
      currentIndex: _currentIndex,
      onBottomBarTap: _onBottomBarTap,
      child: _screens[_currentIndex],
    );
  }
}
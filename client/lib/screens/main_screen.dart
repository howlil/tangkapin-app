import 'package:flutter/material.dart';
import '../layouts/main_layout.dart';
import 'home_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const Center(child: Text('Camera Screen')), // Placeholder
    const Center(child: Text('Reports Screen')), // Placeholder
    const Center(child: Text('Profile Screen')), // Placeholder
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
    return MainLayout(
      title: _titles[_currentIndex],
      showBackButton: false,
      currentIndex: _currentIndex,
      onBottomBarTap: _onBottomBarTap,
      child: _screens[_currentIndex],
    );
  }
}
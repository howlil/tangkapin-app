import 'package:flutter/material.dart';
import '../widgets/custom_bottom_bar.dart';

class MainLayout extends StatelessWidget {
  final Widget child;
  final String title;
  final bool showBackButton;
  final int currentIndex;
  final Function(int) onBottomBarTap;
  final Widget? action;

  const MainLayout({
    super.key,
    required this.child,
    required this.title,
    this.showBackButton = false,
    required this.currentIndex,
    required this.onBottomBarTap,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: showBackButton
            ? IconButton(
                icon: const Icon(
                  Icons.arrow_back,
                  color: Color(0xFF444444),
                ),
                onPressed: () => Navigator.of(context).pop(),
              )
            : null,
        title: Text(
          title,
          style: const TextStyle(
            color: Color(0xFF444444),
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: action != null ? [action!] : null,
      ),
      body: child,
      bottomNavigationBar: CustomBottomBar(
        currentIndex: currentIndex,
        onTap: onBottomBarTap,
      ),
    );
  }
}
import 'package:flutter/material.dart';

class CustomBottomBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const CustomBottomBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF444444),
        borderRadius: BorderRadius.circular(35),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildBottomBarItem(
            icon: Icons.home,
            index: 0,
            isSelected: currentIndex == 0,
          ),
          _buildBottomBarItem(
            icon: Icons.videocam,
            index: 1,
            isSelected: currentIndex == 1,
          ),
          _buildBottomBarItem(
            icon: Icons.assignment,
            index: 2,
            isSelected: currentIndex == 2,
          ),
          _buildBottomBarItem(
            icon: Icons.person,
            index: 3,
            isSelected: currentIndex == 3,
          ),
        ],
      ),
    );
  }

  Widget _buildBottomBarItem({
    required IconData icon,
    required int index,
    required bool isSelected,
  }) {
    return GestureDetector(
      onTap: () => onTap(index),
      child: Container(
        padding: const EdgeInsets.all(12),
        child: Icon(
          icon,
          color: isSelected ? const Color(0xFFE3F553) : Colors.white,
          size: 28,
        ),
      ),
    );
  }
}
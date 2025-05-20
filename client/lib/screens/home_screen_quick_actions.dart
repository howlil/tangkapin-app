import 'package:flutter/material.dart';
import 'dart:ui';
import 'dart:math' as math;

// Quick Actions Grid with improved design
Widget buildQuickActionsGrid({
  required Function() onViewCCTVs,
  required Function() onReports,
  required Function() onAddCCTV,
  required Function() onAddReport,
}) {
  return Column(
    children: [
      Row(
        children: [
          Expanded(
            child: _buildQuickActionItemGlass(
              icon: Icons.videocam,
              label: 'View CCTVs',
              onTap: onViewCCTVs,
              gradient: const LinearGradient(
                colors: [Color(0xFF4A6AFF), Color(0xFF54C2FF)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildQuickActionItemGlass(
              icon: Icons.assignment,
              label: 'Reports',
              onTap: onReports,
              gradient: const LinearGradient(
                colors: [Color(0xFFFFA64A), Color(0xFFFFD154)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildQuickActionItemGlass(
              icon: Icons.add_circle,
              label: 'Add CCTV',
              onTap: onAddCCTV,
              gradient: const LinearGradient(
                colors: [Color(0xFF4AC77F), Color(0xFF54FFB0)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
          ),
        ],
      ),
      const SizedBox(height: 16),
      _buildAddReportQuickAction(onAddReport),
    ],
  );
}

// Quick Action Item with glass effect
Widget _buildQuickActionItemGlass({
  required IconData icon,
  required String label,
  required VoidCallback onTap,
  required Gradient gradient,
}) {
  return GestureDetector(
    onTap: onTap,
    child: Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            spreadRadius: 1,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 16,
            ),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.9),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: const Color(0xFFE3F553).withOpacity(0.4),
                width: 1.5,
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Icon container with gradient
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: gradient,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: gradient.colors.first.withOpacity(0.3),
                        blurRadius: 8,
                        spreadRadius: 1,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: Icon(
                    icon,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(height: 12),
                // Label with animation shine effect
                ShineEffect(
                  child: Text(
                    label,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF444444),
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

// Special Add Report action with accent design
Widget _buildAddReportQuickAction(VoidCallback onTap) {
  return GestureDetector(
    onTap: onTap,
    child: Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 20,
        vertical: 0,
      ),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE3F553), Color(0xFFA1F553)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFE3F553).withOpacity(0.4),
            blurRadius: 12,
            spreadRadius: 0,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(24),
          onTap: onTap,
          splashColor: Colors.white.withOpacity(0.2),
          highlightColor: Colors.white.withOpacity(0.1),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Animated pulse icon
                PulseAnimation(
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 4,
                          spreadRadius: 0,
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.add_box,
                      color: Color(0xFF444444),
                      size: 24,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                const Text(
                  'Add New Report',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF444444),
                  ),
                ),
                const SizedBox(width: 16),
                const Icon(
                  Icons.arrow_forward,
                  color: Color(0xFF444444),
                  size: 20,
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

// Shine animation effect for text
class ShineEffect extends StatefulWidget {
  final Widget child;
  
  const ShineEffect({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  State<ShineEffect> createState() => _ShineEffectState();
}

class _ShineEffectState extends State<ShineEffect> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              colors: [
                Colors.grey.shade500,
                Colors.grey.shade100,
                Colors.grey.shade500,
              ],
              stops: [
                0.0,
                _controller.value,
                1.0,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              tileMode: TileMode.clamp,
            ).createShader(bounds);
          },
          child: widget.child,
        );
      },
    );
  }
}

// Pulse animation for icons
class PulseAnimation extends StatefulWidget {
  final Widget child;
  
  const PulseAnimation({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  State<PulseAnimation> createState() => _PulseAnimationState();
}

class _PulseAnimationState extends State<PulseAnimation> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
    
    _animation = Tween<double>(begin: 1.0, end: 1.05).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _animation,
      child: widget.child,
    );
  }
}
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  // Animation controller
  late AnimationController _controller;
  
  // Animations
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotateAnimation;
  late Animation<double> _opacityAnimation;
  
  @override
  void initState() {
    super.initState();
    
    // Initialize animation controller
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    
    // Setup scale animation (pulsating effect)
    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
    
    // Setup rotation animation
    _rotateAnimation = Tween<double>(begin: 0, end: 0.1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
    
    // Setup opacity animation for the text
    _opacityAnimation = Tween<double>(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeIn,
      ),
    );
    
    // Start animation and repeat it
    _controller.repeat(reverse: true);
    
    // Navigate to login after delay
    _navigateToLogin();
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  _navigateToLogin() async {
    await Future.delayed(const Duration(seconds: 3));
    if (mounted) {
      context.goNamed('login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFE3F553),
              Color(0xFFA1F553),
            ],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Animated Icon
              AnimatedBuilder(
                animation: _controller,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _scaleAnimation.value,
                    child: Transform.rotate(
                      angle: _rotateAnimation.value * math.pi,
                      child: const Icon(
                        Icons.visibility,
                        size: 80,
                        color: Color(0xFF444444),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 16),
              
              // Animated Title
              AnimatedBuilder(
                animation: _controller,
                builder: (context, child) {
                  return Opacity(
                    opacity: _opacityAnimation.value,
                    child: const Text(
                      'Tangkapin',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF444444),
                      ),
                    ),
                  );
                },
              ),
              
              const SizedBox(height: 40),
              
              // Loading dots animation
              const LoadingDots(),
            ],
          ),
        ),
      ),
    );
  }
}

class LoadingDots extends StatefulWidget {
  const LoadingDots({super.key});

  @override
  State<LoadingDots> createState() => _LoadingDotsState();
}

class _LoadingDotsState extends State<LoadingDots> with TickerProviderStateMixin {
  late AnimationController _controller1;
  late AnimationController _controller2;
  late AnimationController _controller3;
  
  late Animation<double> _sizeAnimation1;
  late Animation<double> _sizeAnimation2;
  late Animation<double> _sizeAnimation3;
  
  @override
  void initState() {
    super.initState();
    
    // Initialize controllers with different durations for staggered effect
    _controller1 = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    _controller2 = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    _controller3 = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    
    // Setup size animations for each dot
    _sizeAnimation1 = Tween<double>(begin: 6, end: 12).animate(
      CurvedAnimation(
        parent: _controller1,
        curve: Curves.easeInOut,
      ),
    );
    
    _sizeAnimation2 = Tween<double>(begin: 6, end: 12).animate(
      CurvedAnimation(
        parent: _controller2,
        curve: Curves.easeInOut,
      ),
    );
    
    _sizeAnimation3 = Tween<double>(begin: 6, end: 12).animate(
      CurvedAnimation(
        parent: _controller3,
        curve: Curves.easeInOut,
      ),
    );
    
    // Start animation sequences with delays
    _controller1.repeat(reverse: true);
    Future.delayed(const Duration(milliseconds: 200), () {
      _controller2.repeat(reverse: true);
    });
    Future.delayed(const Duration(milliseconds: 400), () {
      _controller3.repeat(reverse: true);
    });
  }
  
  @override
  void dispose() {
    _controller1.dispose();
    _controller2.dispose();
    _controller3.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // First dot
        AnimatedBuilder(
          animation: _controller1,
          builder: (context, child) {
            return Container(
              width: _sizeAnimation1.value,
              height: _sizeAnimation1.value,
              decoration: const BoxDecoration(
                color: Color(0xFF444444),
                shape: BoxShape.circle,
              ),
            );
          },
        ),
        const SizedBox(width: 10),
        
        // Second dot
        AnimatedBuilder(
          animation: _controller2,
          builder: (context, child) {
            return Container(
              width: _sizeAnimation2.value,
              height: _sizeAnimation2.value,
              decoration: const BoxDecoration(
                color: Color(0xFF444444),
                shape: BoxShape.circle,
              ),
            );
          },
        ),
        const SizedBox(width: 10),
        
        // Third dot
        AnimatedBuilder(
          animation: _controller3,
          builder: (context, child) {
            return Container(
              width: _sizeAnimation3.value,
              height: _sizeAnimation3.value,
              decoration: const BoxDecoration(
                color: Color(0xFF444444),
                shape: BoxShape.circle,
              ),
            );
          },
        ),
      ],
    );
  }
}

// Additional animated elements for more visual interest
class AnimatedBackground extends StatefulWidget {
  final Widget child;
  
  const AnimatedBackground({
    super.key,
    required this.child,
  });
  
  @override
  State<AnimatedBackground> createState() => _AnimatedBackgroundState();
}

class _AnimatedBackgroundState extends State<AnimatedBackground> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 10),
      vsync: this,
    );
    
    _animation = Tween<double>(begin: 0, end: 1).animate(_controller);
    _controller.repeat();
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
        return CustomPaint(
          painter: BackgroundPainter(_animation.value),
          child: widget.child,
        );
      },
    );
  }
}

class BackgroundPainter extends CustomPainter {
  final double animationValue;
  
  BackgroundPainter(this.animationValue);
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.05)
      ..style = PaintingStyle.fill;
    
    for (int i = 0; i < 5; i++) {
      double circleX = size.width * (0.2 + 0.6 * (i / 4));
      double circleY = size.height * (0.3 + math.sin(animationValue * math.pi * 2 + i) * 0.2);
      double radius = size.width * 0.1 * (1 + math.sin(animationValue * math.pi + i) * 0.2);
      
      canvas.drawCircle(Offset(circleX, circleY), radius, paint);
    }
  }
  
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
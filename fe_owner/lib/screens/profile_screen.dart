import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:ui';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _notificationEnabled = true;
  bool _darkModeEnabled = false;
  
  // Background gradient colors
  final List<Color> _gradientColors = [
    const Color(0xFFE3F553).withOpacity(0.3),
    const Color(0xFFA1F553).withOpacity(0.2),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FF),
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text(
          'Profil',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF444444),
          ),
        ),
      ),
      body: Stack(
        children: [
          // Background gradient
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: _gradientColors,
              ),
            ),
          ),
          
          // Profile content
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Profile Info Card - Glassmorphism
                  _buildGlassCard(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Row(
                        children: [
                          // Profile avatar with camera badge
                          Stack(
                            children: [
                              // Avatar
                              CircleAvatar(
                                radius: 40,
                                backgroundColor: const Color(0xFFE3F553),
                                child: const Text(
                                  'AM',
                                  style: TextStyle(
                                    fontSize: 28,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF444444),
                                  ),
                                ),
                              ),
                              
                              // Camera badge
                              Positioned(
                                right: 0,
                                bottom: 0,
                                child: Container(
                                  padding: const EdgeInsets.all(6),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFE3F553),
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: Colors.white,
                                      width: 2,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withOpacity(0.1),
                                        blurRadius: 4,
                                        spreadRadius: 1,
                                      ),
                                    ],
                                  ),
                                  child: const Icon(
                                    Icons.camera_alt,
                                    color: Color(0xFF444444),
                                    size: 16,
                                  ),
                                ),
                              ),
                              
                              // Edit badge
                              Positioned(
                                right: 5,
                                top: 0,
                                child: Container(
                                  padding: const EdgeInsets.all(6),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    shape: BoxShape.circle,
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withOpacity(0.1),
                                        blurRadius: 4,
                                        spreadRadius: 1,
                                      ),
                                    ],
                                  ),
                                  child: const Icon(
                                    Icons.edit,
                                    color: Color(0xFF444444),
                                    size: 16,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(width: 20),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Admin Aciak Mart',
                                  style: TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF444444),
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'admin@aciakmart.com',
                                  style: TextStyle(
                                    fontSize: 14,
                                    color: Colors.grey[700],
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 4,
                                  ),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFE3F553),
                                    borderRadius: BorderRadius.circular(20),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withOpacity(0.05),
                                        blurRadius: 2,
                                        spreadRadius: 0,
                                      ),
                                    ],
                                  ),
                                  child: const Text(
                                    'Administrator',
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w600,
                                      color: Color(0xFF444444),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Account Section
                  const Text(
                    'Akun',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF444444),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildGlassCard(
                    child: Column(
                      children: [
                        _buildMenuTile(
                          icon: Icons.person,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'Informasi Pribadi',
                          onTap: () {
                            // Navigate to personal info
                          },
                        ),
                        _buildDivider(),
                        _buildMenuTile(
                          icon: Icons.shield,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'Keamanan',
                          onTap: () {
                            // Navigate to security
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Preferences Section
                  const Text(
                    'Preferensi',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF444444),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildGlassCard(
                    child: Column(
                      children: [
                        Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 12,
                          ),
                          child: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFE3F553).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Icon(
                                  Icons.notifications,
                                  color: Color(0xFFE3F553),
                                  size: 24,
                                ),
                              ),
                              const SizedBox(width: 16),
                              const Text(
                                'Notifikasi',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w500,
                                  color: Color(0xFF444444),
                                ),
                              ),
                              const Spacer(),
                              Switch(
                                value: _notificationEnabled,
                                onChanged: (value) {
                                  setState(() {
                                    _notificationEnabled = value;
                                  });
                                },
                                activeTrackColor: const Color(0xFFE3F553),
                                activeColor: Colors.white,
                              ),
                            ],
                          ),
                        ),
                        _buildDivider(),
                        _buildMenuTile(
                          icon: Icons.dark_mode,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'Mode Gelap',
                          onTap: () {
                            // Toggle dark mode
                            setState(() {
                              _darkModeEnabled = !_darkModeEnabled;
                            });
                          },
                        ),
                        _buildDivider(),
                        _buildMenuTile(
                          icon: Icons.settings,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'Pengaturan Aplikasi',
                          onTap: () {
                            // Navigate to app settings
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Help & Support Section
                  const Text(
                    'Bantuan & Dukungan',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF444444),
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildGlassCard(
                    child: Column(
                      children: [
                        _buildMenuTile(
                          icon: Icons.help,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'Pusat Bantuan',
                          onTap: () {
                            // Navigate to help center
                          },
                        ),
                        _buildDivider(),
                        _buildMenuTile(
                          icon: Icons.question_answer,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'FAQ',
                          onTap: () {
                            // Navigate to FAQ
                          },
                        ),
                        _buildDivider(),
                        _buildMenuTile(
                          icon: Icons.email,
                          iconColor: const Color(0xFFE3F553),
                          backgroundColor: const Color(0xFFE3F553).withOpacity(0.2),
                          title: 'Hubungi Kami',
                          onTap: () {
                            // Navigate to contact us
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Logout Button - Glassmorphism
                  GestureDetector(
                    onTap: () {
                      _showLogoutDialog(context);
                    },
                    child: _buildGlassCard(
                      border: Border.all(
                        color: Colors.red.withOpacity(0.3),
                        width: 1.5,
                      ),
                      shadow: BoxShadow(
                        color: Colors.red.withOpacity(0.1),
                        blurRadius: 10,
                        spreadRadius: 1,
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.logout,
                              color: Colors.red,
                              size: 24,
                            ),
                            const SizedBox(width: 12),
                            const Text(
                              'Keluar',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                                color: Colors.red,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Glassmorphism Card
  Widget _buildGlassCard({
    required Widget child,
    Border? border,
    BoxShadow? shadow,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.7),
            borderRadius: BorderRadius.circular(20),
            border: border ?? Border.all(
              color: Colors.white.withOpacity(0.2),
              width: 1.5,
            ),
            boxShadow: shadow != null ? [shadow] : [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                spreadRadius: 1,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }

  Widget _buildMenuTile({
    required IconData icon,
    required Color iconColor,
    required Color backgroundColor,
    required String title,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 14,
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: backgroundColor,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: iconColor,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFF444444),
                ),
              ),
            ),
            Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.7),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.arrow_forward_ios,
                color: Color(0xFF444444),
                size: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(
      height: 1,
      thickness: 1,
      indent: 56,
      endIndent: 16,
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: const Text(
          'Keluar',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF444444),
          ),
        ),
        content: const Text(
          'Apakah Anda yakin ingin keluar?',
          style: TextStyle(
            color: Color(0xFF444444),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFF444444),
            ),
            child: const Text(
              'Batal',
              style: TextStyle(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.goNamed('login');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
            ),
            child: const Text(
              'Keluar',
              style: TextStyle(
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
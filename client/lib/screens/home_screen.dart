import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'dart:async';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Timer _timer;
  DateTime _currentTime = DateTime.now();
  
  // For segmented control
  int _selectedStatView = 0;

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _currentTime = DateTime.now();
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  String _formatDate(DateTime time) {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    const days = [
      'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ];
    
    return '${days[time.weekday - 1]}, ${months[time.month - 1]} ${time.day}, ${time.year}';
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoScrollbar(
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16),
            
            // Header Section with iOS-style
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Good Morning',
                      style: TextStyle(
                        fontFamily: '.SF Pro Display',
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: CupertinoColors.black,
                        letterSpacing: -0.5,
                      ),
                    ),
                    Text(
                      'Admin Dashboard',
                      style: TextStyle(
                        fontFamily: '.SF Pro Text',
                        fontSize: 16,
                        color: CupertinoColors.systemGrey,
                        letterSpacing: -0.3,
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    // iOS-style notification button
                    CupertinoButton(
                      padding: EdgeInsets.zero,
                      onPressed: () {},
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          const Icon(
                            CupertinoIcons.bell,
                            size: 26,
                            color: CupertinoColors.black,
                          ),
                          Positioned(
                            right: 0,
                            top: 0,
                            child: Container(
                              padding: const EdgeInsets.all(4),
                              decoration: BoxDecoration(
                                color: CupertinoColors.systemRed,
                                shape: BoxShape.circle,
                              ),
                              constraints: const BoxConstraints(
                                minWidth: 16,
                                minHeight: 16,
                              ),
                              child: const Text(
                                '3',
                                style: TextStyle(
                                  fontFamily: '.SF Pro Text',
                                  color: CupertinoColors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    // iOS-style profile avatar
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE3F553),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: CupertinoColors.systemGrey5,
                            blurRadius: 4,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Center(
                        child: Text(
                          'AD',
                          style: TextStyle(
                            fontFamily: '.SF Pro Text',
                            fontWeight: FontWeight.w600,
                            color: const Color(0xFF444444),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Date and Time Section
            _buildTimeCard(),
            const SizedBox(height: 24),
            
            // Statistics Header with Segmented Control
            Row(
              children: [
                Text(
                  'Statistics',
                  style: TextStyle(
                    fontFamily: '.SF Pro Display',
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: CupertinoColors.black,
                  ),
                ),
                const Spacer(),
                // iOS-style segmented control
                SizedBox(
                  width: 180,
                  child: CupertinoSlidingSegmentedControl<int>(
                    backgroundColor: CupertinoColors.systemGrey6,
                    thumbColor: CupertinoColors.white,
                    groupValue: _selectedStatView,
                    onValueChanged: (int? value) {
                      setState(() {
                        _selectedStatView = value!;
                      });
                    },
                    children: const {
                      0: Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16),
                        child: Text('Daily'),
                      ),
                      1: Padding(
                        padding: EdgeInsets.symmetric(horizontal: 16),
                        child: Text('Weekly'),
                      ),
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Statistics Cards
            Row(
              children: [
                Expanded(
                  child: _buildIOSStatCard(
                    icon: CupertinoIcons.videocam_fill,
                    iconColor: CupertinoColors.activeBlue,
                    count: '12',
                    label: 'Active CCTVs',
                    change: '+2 today',
                    changeColor: CupertinoColors.activeGreen,
                    uptime: '95% uptime',
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildIOSStatCard(
                    icon: CupertinoIcons.exclamationmark_triangle_fill,
                    iconColor: CupertinoColors.systemOrange,
                    count: '8',
                    label: 'Active Reports',
                    change: '+3 today',
                    changeColor: CupertinoColors.systemRed,
                    uptime: '+25% from last week',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            
            // Live Preview Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Live Preview',
                  style: TextStyle(
                    fontFamily: '.SF Pro Display',
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: CupertinoColors.black,
                  ),
                ),
                CupertinoButton(
                  padding: EdgeInsets.zero,
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'View All',
                        style: TextStyle(
                          fontFamily: '.SF Pro Text',
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: CupertinoColors.activeBlue,
                        ),
                      ),
                      const Icon(
                        CupertinoIcons.chevron_right,
                        size: 14,
                        color: CupertinoColors.activeBlue,
                      ),
                    ],
                  ),
                  onPressed: () {},
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // CCTV Preview Card
            _buildCCTVPreviewCard(),
            const SizedBox(height: 16),
            
            // CCTV Details Card
            _buildCCTVDetailsCard(),
            const SizedBox(height: 24),
            
            // Quick Actions Section
            Text(
              'Quick Actions',
              style: TextStyle(
                fontFamily: '.SF Pro Display',
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: CupertinoColors.black,
              ),
            ),
            const SizedBox(height: 16),
            
            // Quick Action Buttons - iOS Style
            _buildQuickActionsGrid(),
            
            const SizedBox(height: 100), // Bottom padding for navigation bar
          ],
        ),
      ),
    );
  }

  // iOS-style Time Card
  Widget _buildTimeCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CupertinoColors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: CupertinoColors.systemGrey5,
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Today',
                style: TextStyle(
                  fontFamily: '.SF Pro Text',
                  fontSize: 14,
                  color: CupertinoColors.systemGrey,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                _formatDate(_currentTime),
                style: TextStyle(
                  fontFamily: '.SF Pro Display',
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: CupertinoColors.black,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFE3F553),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              _formatTime(_currentTime),
              style: TextStyle(
                fontFamily: '.SF Pro Display',
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF444444),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // iOS-style Stat Card
  Widget _buildIOSStatCard({
    required IconData icon,
    required Color iconColor,
    required String count,
    required String label,
    required String change,
    required Color changeColor,
    required String uptime,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CupertinoColors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: CupertinoColors.systemGrey5,
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  icon,
                  color: iconColor,
                  size: 20,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: changeColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  change,
                  style: TextStyle(
                    fontFamily: '.SF Pro Text',
                    color: changeColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            count,
            style: TextStyle(
              fontFamily: '.SF Pro Display',
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: CupertinoColors.black,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontFamily: '.SF Pro Text',
              fontSize: 14,
              color: CupertinoColors.systemGrey,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            uptime,
            style: TextStyle(
              fontFamily: '.SF Pro Text',
              fontSize: 12,
              color: changeColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  // iOS-style CCTV Preview Card
  Widget _buildCCTVPreviewCard() {
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: CupertinoColors.systemGrey6,
        borderRadius: BorderRadius.circular(16),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Container(
              width: double.infinity,
              height: double.infinity,
              color: CupertinoColors.systemGrey4,
              child: const Center(
                child: Icon(
                  CupertinoIcons.videocam,
                  size: 50,
                  color: CupertinoColors.systemGrey,
                ),
              ),
            ),
            // iOS-style overlay elements
            Positioned(
              top: 16,
              left: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: CupertinoColors.black.withOpacity(0.7),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      CupertinoIcons.videocam_fill,
                      color: CupertinoColors.white,
                      size: 14,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'CCTV 1 - Indoor',
                      style: TextStyle(
                        fontFamily: '.SF Pro Text',
                        color: CupertinoColors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Positioned(
              top: 16,
              right: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: CupertinoColors.systemRed,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'Live',
                  style: TextStyle(
                    fontFamily: '.SF Pro Text',
                    color: CupertinoColors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // iOS-style CCTV Details Card
  Widget _buildCCTVDetailsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: CupertinoColors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: CupertinoColors.systemGrey5,
            blurRadius: 10,
            spreadRadius: 0,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Main Store Area',
                style: TextStyle(
                  fontFamily: '.SF Pro Display',
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: CupertinoColors.black,
                ),
              ),
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: CupertinoColors.activeGreen,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'Online (5h)',
                    style: TextStyle(
                      fontFamily: '.SF Pro Text',
                      color: CupertinoColors.activeGreen,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Monitoring customer activity in aisle 3-5',
            style: TextStyle(
              fontFamily: '.SF Pro Text',
              color: CupertinoColors.systemGrey,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Last motion detected: 2 min ago',
                style: TextStyle(
                  fontFamily: '.SF Pro Text',
                  color: CupertinoColors.systemGrey,
                  fontSize: 12,
                ),
              ),
              Row(
                children: [
                  Text(
                    '4 people in view',
                    style: TextStyle(
                      fontFamily: '.SF Pro Text',
                      color: CupertinoColors.black,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Text(
                    'Updated: 5s ago',
                    style: TextStyle(
                      fontFamily: '.SF Pro Text',
                      color: CupertinoColors.systemGrey,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: CupertinoButton(
                  padding: EdgeInsets.zero,
                  onPressed: () {},
                  child: Container(
                    height: 44,
                    decoration: BoxDecoration(
                      color: const Color(0xFFE3F553),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Center(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            CupertinoIcons.eye,
                            size: 16,
                            color: Color(0xFF444444),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'View Details',
                            style: TextStyle(
                              fontFamily: '.SF Pro Text',
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: const Color(0xFF444444),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: CupertinoButton(
                  padding: EdgeInsets.zero,
                  onPressed: () {},
                  child: Container(
                    height: 44,
                    decoration: BoxDecoration(
                      color: CupertinoColors.systemGrey6,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Center(
                      child: Text(
                        'All Cameras',
                        style: TextStyle(
                          fontFamily: '.SF Pro Text',
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: CupertinoColors.black,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // iOS-style Quick Actions Grid
  Widget _buildQuickActionsGrid() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildIOSQuickActionItem(
                icon: CupertinoIcons.videocam_fill,
                label: 'View CCTVs',
                onTap: () {},
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildIOSQuickActionItem(
                icon: CupertinoIcons.doc_text_fill,
                label: 'Reports',
                onTap: () {},
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildIOSQuickActionItem(
                icon: CupertinoIcons.add,
                label: 'Add CCTV',
                onTap: () {},
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        _buildIOSQuickActionItem(
          icon: CupertinoIcons.plus_rectangle_fill,
          label: 'Add New Report',
          onTap: () {},
          isWide: true,
        ),
      ],
    );
  }

  // iOS-style Quick Action Item
  Widget _buildIOSQuickActionItem({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    bool isWide = false,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: isWide ? 200 : null,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: CupertinoColors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: CupertinoColors.systemGrey5,
              blurRadius: 10,
              spreadRadius: 0,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFE3F553),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: const Color(0xFF444444),
                size: 24,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              label,
              style: TextStyle(
                fontFamily: '.SF Pro Text',
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: CupertinoColors.black,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
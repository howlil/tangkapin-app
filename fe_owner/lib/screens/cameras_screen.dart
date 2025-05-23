import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class CamerasScreen extends StatefulWidget {
  const CamerasScreen({super.key});

  @override
  State<CamerasScreen> createState() => _CamerasScreenState();
}

class _CamerasScreenState extends State<CamerasScreen> {
  // Filter state
  String _currentFilter = 'Semua';
  final List<String> _filters = ['Semua', 'Online', 'Offline', 'Maintenance'];
  
  // View type (grid or list)
  bool _isGridView = true;
  
  // Mock data for cameras
  final List<Map<String, dynamic>> _cameras = [
    {
      'id': 'CH01',
      'name': 'Pintu Masuk',
      'location': 'Aciak Mart | Cabang Unand',
      'status': 'Online',
      'uptime': '5 jam',
      'lastMotion': '2 menit lalu',
      'peopleCount': 4,
    },
    {
      'id': 'CH02',
      'name': 'Kasir Utama',
      'location': 'Aciak Mart | Cabang Unand',
      'status': 'Online',
      'uptime': '3 jam',
      'lastMotion': '30 detik lalu',
      'peopleCount': 2,
    },
    {
      'id': 'CH03',
      'name': 'Area Parkir',
      'location': 'Aciak Mart | Cabang Unand',
      'status': 'Offline',
      'uptime': '0',
      'lastMotion': '-',
      'peopleCount': 0,
    },
    {
      'id': 'CH04',
      'name': 'Gudang',
      'location': 'Aciak Mart | Cabang Unand',
      'status': 'Maintenance',
      'uptime': '0',
      'lastMotion': '-',
      'peopleCount': 0,
    },
    {
      'id': 'CH05',
      'name': 'Lorong Makanan',
      'location': 'Aciak Mart | Cabang Unand',
      'status': 'Online',
      'uptime': '8 jam',
      'lastMotion': '5 menit lalu',
      'peopleCount': 1,
    },
    {
      'id': 'CH06',
      'name': 'Lorong Minuman',
      'location': 'Aciak Mart | Cabang Unand',
      'status': 'Online',
      'uptime': '8 jam',
      'lastMotion': '1 menit lalu',
      'peopleCount': 3,
    },
  ];

  // Filtered cameras based on selected filter
  List<Map<String, dynamic>> get _filteredCameras {
    if (_currentFilter == 'Semua') {
      return _cameras;
    }
    return _cameras.where((camera) => camera['status'] == _currentFilter).toList();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Search and Filter Row
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  spreadRadius: 1,
                  blurRadius: 5,
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Cari kamera...',
                      hintStyle: TextStyle(
                        color: Colors.grey[400],
                        fontSize: 14,
                      ),
                      border: InputBorder.none,
                      prefixIcon: const Icon(
                        Icons.search,
                        color: Colors.grey,
                      ),
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE3F553),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.filter_list,
                    color: Color(0xFF444444),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          
          // Filter Chips and View Toggle
          Row(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: _filters.map((filter) {
                      final isSelected = _currentFilter == filter;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          selected: isSelected,
                          label: Text(filter),
                          onSelected: (selected) {
                            setState(() {
                              _currentFilter = filter;
                            });
                          },
                          backgroundColor: Colors.white,
                          selectedColor: const Color(0xFFE3F553),
                          checkmarkColor: const Color(0xFF444444),
                          labelStyle: TextStyle(
                            color: isSelected
                                ? const Color(0xFF444444)
                                : Colors.grey[600],
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(50),
                            side: BorderSide(
                              color: isSelected
                                  ? const Color(0xFFE3F553)
                                  : Colors.grey[300]!,
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              // View Toggle Button
              InkWell(
                onTap: () {
                  setState(() {
                    _isGridView = !_isGridView;
                  });
                },
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: Colors.grey[300]!,
                    ),
                  ),
                  child: Icon(
                    _isGridView ? Icons.view_list : Icons.grid_view,
                    color: const Color(0xFF444444),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Cameras Count
          Text(
            'Menampilkan ${_filteredCameras.length} Kamera',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF444444),
            ),
          ),
          const SizedBox(height: 16),
          
          // Cameras Grid/List View
          _isGridView
              ? _buildGridView()
              : _buildListView(),
              
          const SizedBox(height: 100), // Bottom padding for navigation bar
        ],
      ),
    );
  }

  Widget _buildGridView() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 0.85,
      ),
      itemCount: _filteredCameras.length,
      itemBuilder: (context, index) {
        final camera = _filteredCameras[index];
        return _buildCameraGridItem(camera);
      },
    );
  }

  Widget _buildListView() {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _filteredCameras.length,
      itemBuilder: (context, index) {
        final camera = _filteredCameras[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: _buildCameraListItem(camera),
        );
      },
    );
  }

  Widget _buildCameraGridItem(Map<String, dynamic> camera) {
    Color statusColor;
    
    switch (camera['status']) {
      case 'Online':
        statusColor = Colors.green;
        break;
      case 'Offline':
        statusColor = Colors.red;
        break;
      case 'Maintenance':
        statusColor = Colors.amber;
        break;
      default:
        statusColor = Colors.grey;
    }
    
    return InkWell(
      onTap: () {
        context.pushNamed('camera_details', pathParameters: {'id': camera['id']});
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              spreadRadius: 1,
              blurRadius: 5,
            ),
          ],
        ),
        child: Column(
          children: [
            // Camera Preview
            ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
              child: Stack(
                children: [
                  Container(
                    height: 120,
                    width: double.infinity,
                    color: Colors.grey[400],
                    child: const Center(
                      child: Icon(
                        Icons.videocam,
                        color: Colors.white,
                        size: 40,
                      ),
                    ),
                  ),
                  // Camera ID Label
                  Positioned(
                    top: 8,
                    left: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.6),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        '${camera['id']}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                  // Status Badge
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: camera['status'] == 'Online' ? Colors.red : Colors.grey[600],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        camera['status'] == 'Online' ? 'Live' : camera['status'],
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Camera Info
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${camera['name']}',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF444444),
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${camera['location']}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          color: statusColor,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${camera['status']}',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: statusColor,
                        ),
                      ),
                      const SizedBox(width: 8),
                      if (camera['status'] == 'Online')
                        Text(
                          '(${camera['uptime']})',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCameraListItem(Map<String, dynamic> camera) {
    Color statusColor;
    
    switch (camera['status']) {
      case 'Online':
        statusColor = Colors.green;
        break;
      case 'Offline':
        statusColor = Colors.red;
        break;
      case 'Maintenance':
        statusColor = Colors.amber;
        break;
      default:
        statusColor = Colors.grey;
    }
    
    return InkWell(
      onTap: () {
        context.pushNamed('camera_details', pathParameters: {'id': camera['id']});
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              spreadRadius: 1,
              blurRadius: 5,
            ),
          ],
        ),
        child: Row(
          children: [
            // Camera Preview
            ClipRRect(
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                bottomLeft: Radius.circular(16),
              ),
              child: Stack(
                children: [
                  Container(
                    height: 120,
                    width: 100,
                    color: Colors.grey[400],
                    child: const Center(
                      child: Icon(
                        Icons.videocam,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ),
                  // Status Badge
                  Positioned(
                    top: 8,
                    left: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: camera['status'] == 'Online' ? Colors.red : Colors.grey[600],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        camera['status'] == 'Online' ? 'Live' : camera['status'],
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 8,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // Camera Info
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${camera['id']} - ${camera['name']}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF444444),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${camera['location']}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: statusColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${camera['status']}',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: statusColor,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    if (camera['status'] == 'Online') ...[
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Uptime: ${camera['uptime']}',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          Text(
                            '${camera['peopleCount']} orang terdeteksi',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w500,
                              color: Color(0xFF444444),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
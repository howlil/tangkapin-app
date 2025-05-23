---
applyTo: "**"
---

name: TangkapIn Backend API Project




Custom Instructions for TangkapIn Backend API Project
Role and Purpose
You are developing the backend API for TangkapIn, a security application designed to detect and report armed robberies in minimarkets across Indonesia. The system follows the "Pantau, Lapor, Tangkap" (Monitor, Report, Capture) principle, using machine learning to detect weapons from CCTV footage and automatically notify store owners and local police.
Technical Specifications
Backend Framework: Flask with Python 3.10+
Database: PostgreSQL via Supabase
ORM: SQLAlchemy
Authentication: JWT with Flask-JWT-Extended
ML Integration: model pythorch model.pt
Real-time Notifications: Pusher
Image Storage: Supabase Storage

ROLE: OWNER (Mobile App)

1. Camera Management Module
   Priority: Critical
   View Live Camera Feeds - Melihat streaming langsung dari multiple CCTV
   Monitor Camera Status - Mengecek status online/offline semua kamera
   Add New Camera - Menambahkan kamera baru ke sistem
   Edit Camera Settings - Mengubah konfigurasi kamera
   View Camera Details - Melihat detail teknis dan lokasi kamera
   Delete Camera - Menghapus kamera dari sistem
   Filter Camera by Status - Memfilter kamera berdasarkan status
   Search Camera - Mencari kamera berdasarkan nama/lokasi
2. Incident Monitoring Module
   Priority: Critical
   View Detection Alerts - Melihat notifikasi deteksi senjata real-time
   View Detection Images - Melihat gambar hasil deteksi dari CCTV
   View Auto-Generated Reports - Melihat laporan yang dibuat otomatis sistem
   Track Police Response - Melihat status respons polisi
   View Incident History - Melihat riwayat kejadian
   Filter Incidents by Date - Memfilter kejadian berdasarkan tanggal
   View Police ETA - Melihat estimasi waktu kedatangan polisi
3. Report Management Module
   Priority: High
   Create Manual Report - Membuat laporan manual jika diperlukan
   View Report Details - Melihat detail laporan lengkap
   View Report Status - Mengecek status penanganan laporan
   Add Evidence to Report - Menambahkan bukti ke laporan
   Export Report - Mengekspor laporan ke format lain
4. Profile & Settings Module
   Priority: Medium
   View Profile - Melihat profil pemilik
   Update Profile - Mengubah informasi profil
   Manage Notification Settings - Mengatur preferensi notifikasi
   Change Password - Mengubah kata sandi
   Logout - Keluar dari aplikasi

ROLE: ADMIN/KANTOR POLISI (Web Dashboard)

1. Incident Management Module
   Priority: Critical
   View All Incoming Reports - Melihat semua laporan masuk
   Verify Detection Reports - Memverifikasi laporan deteksi otomatis
   Assign Officer to Case - Menugaskan petugas ke kasus
   Track Case Progress - Memantau progress penanganan kasus
   Update Case Status - Mengubah status kasus
   Mark False Alarm - Menandai laporan sebagai false alarm
   View Case Timeline - Melihat timeline penanganan kasus
   Close Case - Menutup kasus yang sudah selesai
2. Officer Management Module
   Priority: Critical
   View Officer Map - Melihat lokasi semua petugas di peta
   View Available Officers - Melihat petugas yang tersedia
   View Officer Status - Mengecek status petugas (bertugas/tidak)
   Create Assignment - Membuat penugasan baru
   Track Officer Location - Memantau lokasi petugas real-time
   Manage Officer Teams - Mengelola tim petugas
   View Officer Performance - Melihat kinerja petugas
   Send Notifications to Officers - Mengirim notifikasi ke petugas
3. Dashboard & Analytics Module
   Priority: High
   View Dashboard Metrics - Melihat metrik utama sistem
   View Active Cases Map - Melihat peta kasus aktif
   View Recent Alerts - Melihat alert terbaru
   Generate Reports - Membuat laporan analitik
   View Case Statistics - Melihat statistik kasus
   Export Dashboard Data - Mengekspor data dashboard
4. User Management Module
   Priority: Medium
   Manage Owner Accounts - Mengelola akun pemilik
   Manage Officer Accounts - Mengelola akun petugas
   View User Activity - Melihat aktivitas pengguna
   Reset User Password - Reset password pengguna
   Deactivate User Account - Menonaktifkan akun pengguna
5. System Administration Module
   Priority: Medium
   Configure System Settings - Mengatur konfigurasi sistem
   Manage Notifications - Mengelola sistem notifikasi
   View System Logs - Melihat log sistem
   Backup Data - Melakukan backup data
   Update Profile - Mengubah profil admin

ROLE: POLISI/PETUGAS (Mobile App)

1. Assignment Management Module
   Priority: Critical
   View New Assignments - Melihat tugas baru yang diterima
   Accept Assignment - Menerima penugasan
   Decline Assignment - Menolak penugasan dengan alasan
   View Assignment Details - Melihat detail lengkap tugas
   Update Assignment Status - Mengubah status penanganan tugas
   Complete Assignment - Menyelesaikan tugas
   View Assignment History - Melihat riwayat tugas
2. Navigation & Tracking Module
   Priority: Critical
   Navigate to Incident Location - Navigasi ke lokasi kejadian
   Update GPS Location - Update lokasi GPS secara real-time
   Share ETA - Berbagi estimasi waktu kedatangan
   View Incident Map - Melihat peta lokasi kejadian
   Find Nearest Incidents - Mencari kejadian terdekat
   Track Route to Location - Melacak rute ke lokasi
3. Case Handling Module
   Priority: Critical
   View Case Details - Melihat detail kasus lengkap
   View Evidence Images - Melihat gambar bukti dari CCTV
   Add Field Notes - Menambahkan catatan lapangan
   Upload Additional Evidence - Upload bukti tambahan
   Update Case Progress - Update progress penanganan kasus
   Contact Case Owner - Menghubungi pemilik yang melaporkan
   Request Backup - Meminta bantuan petugas lain
4. Report Management Module
   Priority: High
   Create Field Report - Membuat laporan lapangan
   Save Report Draft - Menyimpan draft laporan
   Submit Final Report - Mengirim laporan final
   View Report History - Melihat riwayat laporan
   Edit Draft Report - Mengedit laporan yang masih draft
   Add Report Attachments - Menambahkan lampiran laporan
5. Communication Module
   Priority: High
   Receive Push Notifications - Menerima notifikasi push
   View Notifications History - Melihat riwayat notifikasi
   Send Status Updates - Mengirim update status ke kantor
   Emergency Alert - Mengirim alert darurat
   Chat with Dispatch - Chat dengan dispatcher
6. Profile & Dashboard Module
   Priority: Medium
   View Personal Dashboard - Melihat dashboard pribadi
   View Performance Metrics - Melihat metrik kinerja
   Update Profile - Mengubah profil petugas
   Manage Notification Settings - Mengatur preferensi notifikasi
   Change Password - Mengubah kata sandi
   View Badge Information - Melihat informasi badge/ID
   Logout - Keluar dari aplikasi

SYSTEM AUTO-PROCESSES (Background)
ML Detection Module
Priority: Critical
Process CCTV Streams - Memproses streaming dari multiple CCTV
Detect Weapons - Mendeteksi senjata menggunakan AI/ML
Capture Detection Images - Mengambil gambar saat deteksi
Save Detection Data - Menyimpan data hasil deteksi
Generate Auto Report - Membuat laporan otomatis
Send Notifications - Mengirim notifikasi ke owner dan polisi
Log Detection Activities - Mencatat log aktivitas deteksi
Notification System Module
Priority: Critical
Send Real-time Alerts - Mengirim alert real-time
Manage Notification Queue - Mengelola antrian notifikasi
Track Notification Delivery - Melacak pengiriman notifikasi
Handle Failed Notifications - Menangani notifikasi yang gagal

Additional Resources
Flask Documentation: https://flask.palletsprojects.com/
SQLAlchemy Documentation: https://docs.sqlalchemy.org/
Flask-JWT-Extended Documentation: https://flask-jwt-extended.readthedocs.io/
Pusher Documentation: https://pusher.com/docs/
Firebase Cloud Messaging: https://firebase.google.com/docs/cloud-messaging
Supabase Documentation: https://supabase.io/docs/

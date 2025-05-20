import React from 'react';

const PopupNotification = ({ notification, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
        <h2 className="text-xl font-bold mb-2">Notifikasi Baru</h2>
        <p className="text-sm text-gray-700">
          <strong>Tipe:</strong> {notification.type}
        </p>
        <p className="text-sm text-gray-700">
          <strong>Pelapor:</strong> {notification.owner_name} ({notification.owner_address})
        </p>
        <p className="text-sm text-gray-700">
          <strong>Jarak ke Lokasi:</strong> {notification.distance_km} km
        </p>
        {notification.images && notification.images.length > 0 && (
          <img
            src={notification.images[0]}
            alt="Evidence"
            className="w-full h-40 object-cover rounded-lg mt-2"
          />
        )}
        <p className="text-sm text-gray-500 mt-2">
          <strong>Waktu:</strong> {new Date(notification.timestamp).toLocaleString()}
        </p>
        <button
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
          onClick={onClose}
        >
          Tutup
        </button>
      </div>
    </div>
  );
};

export default PopupNotification;

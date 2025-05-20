import React, { useState, useEffect } from 'react';
import { initPusher, subscribeToChannel } from '../../utils/pusher';
import PopupNotification from '../PopupNotification';

const PusherLayout = ({ children }) => {
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    // Inisialisasi Pusher
    const pusher = initPusher('ef6ded14f456b73f9a12', 'ap1');

    // Berlangganan ke saluran dan event
    const unsubscribe = subscribeToChannel('police', 'incident_alert', (data) => {
      setNotification(data); // Menyimpan seluruh data notifikasi
    });

    // Cleanup saat komponen di-unmount
    return () => {
      unsubscribe();
    };
  }, []);

  const handleCloseNotification = () => {
    setNotification(null); // Tutup pop-up
  };

  return (
    <div>
      {children}
      {notification && (
        <PopupNotification notification={notification} onClose={handleCloseNotification} />
      )}
    </div>
  );
};

export default PusherLayout;

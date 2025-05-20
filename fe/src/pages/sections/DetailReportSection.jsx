import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/Card';
import { MapPin, Calendar, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import api from "../../utils/api"
import { useParams } from 'react-router-dom';

const DetailReportSection = ({ data }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const { predict_id } = useParams()


  useEffect(() => {
    if (data) {
      setIsLoading(false);
    }
  }, [data]);

  const nextImage = () => {
    if (!data?.predict?.images?.length) return;
    setCurrentImageIndex((prev) =>
      prev === data.predict.images.length - 1 ? 0 : prev + 1
    );
  };

  const prevImage = () => {
    if (!data?.predict?.images?.length) return;
    setCurrentImageIndex((prev) =>
      prev === 0 ? data.predict.images.length - 1 : prev - 1
    );
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'dd MMMM yyyy');
    } catch (error) {
      return '-';
    }
  };

  const formatTime = (dateString) => {
    try {
      return format(new Date(dateString), 'HH:mm');
    } catch (error) {
      return '-';
    }
  };
  const openConfirmPopup = () => {
    setIsConfirmOpen(true);
  };

  const closeConfirmPopup = () => {
    setIsConfirmOpen(false);
  };
  const updateStatus = async () => {
    try {
      setStatusLoading(true);

      // Tentukan status berikutnya berdasarkan status saat ini
      const currentStatus = data.status;
      let nextStatus = '';
      if (currentStatus === 'PENDING') {
        nextStatus = 'DIPROSES';
      } else if (currentStatus === 'DIPROSES') {
        nextStatus = 'SELESAI';
      } else {
        alert('Status tidak dapat diubah lebih lanjut.');
        setStatusLoading(false);
        return;
      }

      // Kirim permintaan PATCH ke API dengan status baru
      const response = await api.patch(`/api/v1/reports/${predict_id}`, {
        status: nextStatus,
      });

      if (response.status === 200) {
        alert(`Status berhasil diperbarui ke ${nextStatus}!`);
        setData((prevData) => ({
          ...prevData,
          status: nextStatus,
        }));
      } else {
        alert('Gagal memperbarui status.');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Terjadi kesalahan. Silakan coba lagi.');
    } finally {
      setStatusLoading(false);
      closeConfirmPopup();
    }
  };

  if (!data || !data.predict) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="w-full bg-white shadow-lg">
          <CardContent className="p-6">
            <p className="text-center text-gray-600">Data tidak tersedia</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-gray-600" />
      </div>
    );
  }

  if (!data || !data.predict) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="w-full bg-white shadow-lg">
          <CardContent className="p-6">
            <p className="text-center text-gray-600">Data tidak tersedia</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 ">
      <Card className="w-full bg-white shadow-lg">
        <CardHeader className="border-b">
          <CardTitle className="text-2xl font-bold text-red-600 flex items-center gap-2">
            <AlertCircle className="w-6 h-6" />
            Laporan Perampokan
          </CardTitle>
        </CardHeader>

        <CardContent className="p-6">
          {/* Image Slider */}
          <div className="relative w-full h-96 mb-8 rounded-lg overflow-hidden">
            {data?.predict?.images?.length > 0 ? (
              <>
                <img
                  src={data.predict.images[currentImageIndex].name_image}
                  alt={`Evidence ${currentImageIndex + 1}`}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 flex items-center justify-between p-4">
                  <button
                    onClick={prevImage}
                    className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition"
                  >
                    ❮
                  </button>
                  <button
                    onClick={nextImage}
                    className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition"
                  >
                    ❯
                  </button>
                </div>
                <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2">
                  {data.predict.images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentImageIndex(index)}
                      className={`w-3 h-3 rounded-full ${index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                        }`}
                    />
                  ))}
                </div>
              </>
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gray-100">
                <p className="text-gray-500">Tidak ada gambar tersedia</p>
              </div>
            )}
          </div>

          {/* Status Badge */}
          <div className="mb-6">
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${data.status === 'PENDING' ? 'bg-yellow-400 text-black' :
              data.status === 'DIPROSES' ? 'bg-orange-400 text-black' : data.status === 'SELESAI' ? 'bg-green-400 text-black' :
                'bg-red-100 text-red-800'
              }`}>
              {data.status || 'UNKNOWN'}
            </span>
          </div>

          {/* Description */}
          <div className="space-y-6">
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-2">Deskripsi Kejadian</h3>
              <p className="text-gray-700">{data.predict.deskripsi || 'Tidak ada deskripsi'}</p>
            </div>

            {/* Location Details */}
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                Lokasi Kejadian
              </h3>
              <div className="space-y-2">
                <p className="text-gray-700">
                  <span className="font-medium">Nama:</span> {data.user?.name || '-'}
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Alamat:</span> {data.user?.address || '-'}
                </p>

              </div>
            </div>

            {/* Time Details */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-gray-600" />
                <span className="text-gray-700">
                  Tanggal: {formatDate(data.created_at)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-gray-600" />
                <span className="text-gray-700">
                  Waktu: {formatTime(data.created_at)}
                </span>
              </div>
            </div>
          </div>
          {data.status === 'SELESAI' ? null :
            (
              <>
                <div className="mt-8 flex justify-end">
                  <button
                    onClick={openConfirmPopup}
                    className="bg-yellow-400  text-black px-6 py-3 rounded-lg "
                  >
                    Ubah Status
                  </button>
                </div>
              </>
            )
          }

        </CardContent>
      </Card>
      {isConfirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="text-lg font-semibold mb-4">Konfirmasi</h3>
            <p className="mb-6">
              Apakah Anda yakin ingin mengubah status
            </p>
            <div className="flex justify-end gap-4">
              <button
                onClick={closeConfirmPopup}
                className="bg-gray-300 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-400"
              >
                Batal
              </button>
              <button
                onClick={updateStatus}
                disabled={statusLoading}
                className="bg-yellow-400 text-black px-4 py-2 rounded-lg  disabled:opacity-50"
              >
                {statusLoading ? 'Memproses...' : 'Konfirmasi'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DetailReportSection;
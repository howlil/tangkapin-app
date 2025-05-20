import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../utils/api";
import DashboardLayout from "../components/layouts/DashboardLayout";

const Reports = () => {
    const [data, setData] = useState([]);
    const location = useLocation();
    const navigate = useNavigate();

    // Ambil status dari query parameter
    const queryParams = new URLSearchParams(location.search);
    const statusFromQuery = queryParams.get("status") || "PENDING"; // Default ke "PENDING"
    const [activeTab, setActiveTab] = useState(statusFromQuery.toUpperCase());

    useEffect(() => {
        async function fetchData() {
            try {
                const { data } = await api.get("/api/v2/reports");
                setData(data.data);
            } catch (error) {
                console.log(error);
            }
        }
        fetchData();
    }, []);

    // Update activeTab saat URL berubah
    useEffect(() => {
        const queryStatus = queryParams.get("status") || "PENDING";
        setActiveTab(queryStatus.toUpperCase());
    }, [location.search]);

    const handleTabChange = (status) => {
        // Update URL dengan query parameter baru
        navigate(`/reports?status=${status.toLowerCase()}`);
    };

    const tabs = [
        { id: "SELESAI", label: "Selesai", bgColor: "bg-green-400" },
        { id: "DIPROSES", label: "Proses", bgColor: "bg-orange-400" },
        { id: "PENDING", label: "Pending", bgColor: "bg-yellow-400" },
    ];

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return {
            date: date.toLocaleDateString('id-ID', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            }),
            time: date.toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            })
        };
    };

    const renderCards = () => {
        const filteredData = data.filter(item =>
            item.status.toUpperCase() === activeTab
        );

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
                {filteredData.map((item) => {
                    const { date, time } = formatDate(item.created_at);
                    return (
                        <div
                            onClick={() => window.location.href = `/reports/${item.id}`}
                            key={item.id}
                            className="bg-white rounded-lg shadow overflow-hidden transition-shadow hover:shadow-md"
                        >
                            <div className="relative">
                                {item.predict.images && item.predict.images.length > 0 && (
                                    <img
                                        src={item.predict.images[0].name_image}
                                        alt="Report thumbnail"
                                        className="w-full h-48 object-cover"
                                    />
                                )}

                            </div>
                            <div className="p-2">
                                <div className="flex  justify-between items-center">
                                    <span>{date}</span>
                                    <span>{time}</span>
                                </div>
                                <span className={`inline-block px-3 py-1 rounded-full text-sm ${activeTab === "SELESAI" ? "bg-green-400" :
                                    activeTab === "DIPROSES" ? "bg-orange-400" :
                                        "bg-yellow-400"
                                    }`}>
                                    {item.status}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <DashboardLayout>
            <div className="min-h-screen">
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-4 px-4 py-2">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => handleTabChange(tab.id)}
                                className={`px-4 py-2 rounded-md ${activeTab === tab.id
                                    ? `${tab.bgColor} font-medium`
                                    : "text-gray-500 hover:text-gray-700"
                                    }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>
                {renderCards()}
            </div>
        </DashboardLayout>
    );
};

export default Reports;

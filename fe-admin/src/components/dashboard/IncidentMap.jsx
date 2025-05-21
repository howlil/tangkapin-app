import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import useDashboardStore from '../../store/dashboardStore';
import { LuMapPin, LuShield, LuAlertTriangle } from 'react-icons/lu';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for marker icons in Leaflet with webpack/vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

// Custom icons
const createCustomIcon = (color) => {
    return L.divIcon({
        className: 'custom-icon',
        html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid white;"></div>`,
        iconSize: [24, 24],
    });
};

const redIcon = createCustomIcon('#ef4444');
const blueIcon = createCustomIcon('#3b82f6');
const yellowIcon = createCustomIcon('#eab308');

const MapCenter = ({ center }) => {
    const map = useMap();

    useEffect(() => {
        if (center) {
            map.setView(center, map.getZoom());
        }
    }, [center, map]);

    return null;
};

const IncidentMap = () => {
    const { incidents, officers } = useDashboardStore();
    const [mapCenter, setMapCenter] = useState([37.7749, -122.4194]);

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Current Incident Map</CardTitle>
                <CardDescription>Crime locations and active officers</CardDescription>
            </CardHeader>
            <CardContent className="p-0 h-[500px]">
                <MapContainer
                    center={mapCenter}
                    zoom={13}
                    className="h-full w-full"
                    style={{ background: '#f5f5f5' }}
                >
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />

                    <MapCenter center={mapCenter} />

                    {/* Active Incidents */}
                    {incidents.map((incident) => (
                        <Marker
                            key={`incident-${incident.id}`}
                            position={[incident.lat, incident.lng]}
                            icon={incident.priority === 'High' ? redIcon : yellowIcon}
                        >
                            <Popup>
                                <div className="p-2">
                                    <div className="flex items-center">
                                        <LuAlertTriangle className="text-red-500 mr-2" />
                                        <span className="font-semibold">{incident.status} Incident</span>
                                    </div>
                                    <p className="font-medium">{incident.type}</p>
                                    <p className="text-sm text-neutral-600">{incident.location}</p>
                                    <p className="text-xs text-neutral-500 mt-1">{incident.time}</p>
                                    <button className="bg-neutral-100 hover:bg-neutral-200 text-xs rounded px-2 py-1 mt-2">
                                        Assign
                                    </button>
                                    <button className="bg-neutral-100 hover:bg-neutral-200 text-xs rounded px-2 py-1 mt-2 ml-2">
                                        Details
                                    </button>
                                </div>
                            </Popup>
                        </Marker>
                    ))}

                    {/* Officers */}
                    {officers.map((officer) => (
                        <Marker
                            key={`officer-${officer.id}`}
                            position={[officer.location.lat, officer.location.lng]}
                            icon={blueIcon}
                        >
                            <Popup>
                                <div className="p-2">
                                    <div className="flex items-center">
                                        <LuShield className="text-blue-500 mr-2" />
                                        <span className="font-semibold">{officer.name}</span>
                                    </div>
                                    <p className="text-sm text-neutral-600">{officer.unit}</p>
                                    <p className="text-xs text-neutral-500 mt-1">Status: {officer.status}</p>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>

                <div className="absolute bottom-4 left-4 bg-white p-3 rounded-md shadow-sm z-[400]">
                    <div className="flex flex-col gap-2">
                        <div className="flex items-center">
                            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                            <span className="text-xs">Active Incidents</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
                            <span className="text-xs">Verified Incidents</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                            <span className="text-xs">Officers</span>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default IncidentMap; 
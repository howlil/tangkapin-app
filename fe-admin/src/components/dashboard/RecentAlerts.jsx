import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { LuAlertTriangle, LuClock, LuShield, LuCheckCircle } from 'react-icons/lu';
import useDashboardStore from '../../store/dashboardStore';

const alertTypeIcons = {
    'Armed Robbery': LuAlertTriangle,
    'Verification Required': LuClock,
    'Officers Arrived': LuShield,
    'Case Closed': LuCheckCircle,
};

const alertTypeBadge = {
    'Armed Robbery': { variant: 'destructive', label: 'Emergency' },
    'Verification Required': { variant: 'warning', label: 'Attention' },
    'Officers Arrived': { variant: 'secondary', label: 'Info' },
    'Case Closed': { variant: 'success', label: 'Success' },
};

const AlertItem = ({ type, location, time, onViewDetails }) => {
    const Icon = alertTypeIcons[type] || LuAlertTriangle;
    const badge = alertTypeBadge[type] || { variant: 'default', label: 'Alert' };

    return (
        <div className="border-b border-neutral-200 last:border-none py-4">
            <div className="flex items-start gap-3">
                <div className={`p-2 rounded-full ${type === 'Armed Robbery' ? 'bg-red-100' : type === 'Verification Required' ? 'bg-yellow-100' : type === 'Officers Arrived' ? 'bg-blue-100' : 'bg-green-100'}`}>
                    <Icon className={`h-5 w-5 ${type === 'Armed Robbery' ? 'text-red-500' : type === 'Verification Required' ? 'text-yellow-500' : type === 'Officers Arrived' ? 'text-blue-500' : 'text-green-500'}`} />
                </div>

                <div className="flex-1">
                    <div className="flex items-center justify-between">
                        <h4 className="font-medium">{type}</h4>
                        <Badge variant={badge.variant}>{badge.label}</Badge>
                    </div>
                    <p className="text-sm text-neutral-600 mt-1">{location}</p>
                    <p className="text-xs text-neutral-500 mt-2">{time}</p>
                </div>
            </div>

            <div className="flex justify-end mt-3">
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onViewDetails}
                    className="text-xs"
                >
                    Details
                </Button>
            </div>
        </div>
    );
};

const RecentAlerts = () => {
    const { incidents } = useDashboardStore();

    // Convert incidents to alerts format
    const alerts = [
        { id: 1, type: 'Armed Robbery', location: '7-Eleven Main St. #123', time: '5 minutes ago' },
        { id: 2, type: 'Verification Required', location: 'Circle K Broadway #45', time: '15 minutes ago' },
        { id: 3, type: 'Officers Arrived', location: 'QuickMart Central Ave #67', time: '25 minutes ago' },
        { id: 4, type: 'Case Closed', location: 'MiniStop Oak St. #89', time: '1 hour ago' },
    ];

    const handleViewDetails = (id) => {
        console.log(`View details for alert ${id}`);
    };

    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>Important warnings and notifications</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-0">
                    {alerts.map((alert) => (
                        <AlertItem
                            key={alert.id}
                            type={alert.type}
                            location={alert.location}
                            time={alert.time}
                            onViewDetails={() => handleViewDetails(alert.id)}
                        />
                    ))}
                </div>

                <Button variant="ghost" className="w-full mt-4">
                    View All Notifications
                </Button>
            </CardContent>
        </Card>
    );
};

export default RecentAlerts; 
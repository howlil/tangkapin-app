import { LuAlertTriangle, LuUsers, LuCheckCircle, LuClock } from 'react-icons/lu';
import { Card, CardContent } from '../ui/card';

const iconMap = {
    'newReports': LuAlertTriangle,
    'activeOfficers': LuUsers,
    'resolvedCases': LuCheckCircle,
    'responseTime': LuClock,
};

const colorMap = {
    'newReports': 'text-yellow-500',
    'activeOfficers': 'text-blue-500',
    'resolvedCases': 'text-green-500',
    'responseTime': 'text-cyan-500',
};

const StatCard = ({ type, value, label, subtext }) => {
    const Icon = iconMap[type] || LuAlertTriangle;
    const iconColor = colorMap[type] || 'text-neutral-500';

    return (
        <Card className="overflow-hidden">
            <CardContent className="p-6 flex flex-col h-full">
                <div className="flex items-center justify-between mb-4">
                    <Icon className={`h-6 w-6 ${iconColor}`} />
                </div>
                <div>
                    <div className="text-3xl font-bold">{value}</div>
                    <div className="text-sm text-neutral-500 mt-1">{label}</div>
                    {subtext && (
                        <div className="text-xs text-neutral-400 mt-4">{subtext}</div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
};

export default StatCard; 
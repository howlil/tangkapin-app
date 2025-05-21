import { useState } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import StatCard from './StatCard';
import IncidentMap from './IncidentMap';
import RecentAlerts from './RecentAlerts';
import CrimeReportTable from './CrimeReportTable';
import CaseManagement from './CaseManagement';
import OfficerAssignment from './OfficerAssignment';
import useDashboardStore from '../../store/dashboardStore';

const tabData = [
    { id: 'overview', label: 'Overview' },
    { id: 'crimeReports', label: 'Crime Reports' },
    { id: 'officerAssignment', label: 'Officer Assignment' },
    { id: 'caseManagement', label: 'Case Management' },
    { id: 'analytics', label: 'Analytics & Intelligence' },
];

const Dashboard = () => {
    const { stats } = useDashboardStore();
    const [activeTab, setActiveTab] = useState('overview');

    const handleTabChange = (tabId) => {
        setActiveTab(tabId);
    };

    return (
        <div className="space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    type="newReports"
                    value={stats.newReports}
                    label="New Reports"
                    subtext={`+3 in the last 24 hours`}
                />
                <StatCard
                    type="activeOfficers"
                    value={stats.activeOfficers}
                    label="Active Officers"
                    subtext={`8 currently on field duty`}
                />
                <StatCard
                    type="resolvedCases"
                    value={`${stats.resolvedCases}%`}
                    label="Resolved Cases"
                    subtext={`+2% from last month`}
                />
                <StatCard
                    type="responseTime"
                    value={`${stats.responseTime} min`}
                    label="Response Time"
                    subtext={`-1.2 min from average`}
                />
            </div>

            {/* Tabs */}
            <div className="bg-white rounded-lg border border-neutral-200 p-1">
                <div className="flex overflow-x-auto">
                    {tabData.map((tab) => (
                        <Button
                            key={tab.id}
                            variant={activeTab === tab.id ? "default" : "ghost"}
                            className="rounded-md"
                            onClick={() => handleTabChange(tab.id)}
                        >
                            {tab.label}
                        </Button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div>
                {activeTab === 'overview' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2">
                            <IncidentMap />
                        </div>
                        <div>
                            <RecentAlerts />
                        </div>
                    </div>
                )}

                {activeTab === 'crimeReports' && (
                    <CrimeReportTable />
                )}

                {activeTab === 'officerAssignment' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2">
                            <IncidentMap />
                        </div>
                        <div>
                            <OfficerAssignment />
                        </div>
                    </div>
                )}

                {activeTab === 'caseManagement' && (
                    <CaseManagement />
                )}

                {activeTab === 'analytics' && (
                    <div className="space-y-6">
                        <Card className="p-6">
                            <h3 className="text-lg font-medium mb-2">Crime Trend Analysis</h3>
                            <p className="text-neutral-500">Crime patterns and trends in the last 30 days</p>
                            <div className="h-[300px] flex items-center justify-center text-neutral-400">
                                Analytics charts will be implemented here
                            </div>
                        </Card>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <Card className="p-6">
                                <h3 className="text-lg font-medium mb-2">Crime Hotspots</h3>
                                <p className="text-neutral-500">Areas with highest crime rates</p>
                                <div className="h-[300px] flex items-center justify-center text-neutral-400">
                                    Heatmap will be implemented here
                                </div>
                            </Card>

                            <Card className="p-6">
                                <h3 className="text-lg font-medium mb-2">Performance Metrics</h3>
                                <p className="text-neutral-500">Crime handling performance statistics</p>
                                <div className="grid grid-cols-2 gap-4 mt-6">
                                    <div className="bg-neutral-50 p-4 rounded-lg">
                                        <p className="text-sm text-neutral-500">Response Time</p>
                                        <p className="text-2xl font-bold">{stats.responseTime} min</p>
                                    </div>
                                    <div className="bg-neutral-50 p-4 rounded-lg">
                                        <p className="text-sm text-neutral-500">Resolution Rate</p>
                                        <p className="text-2xl font-bold">{stats.resolvedCases}%</p>
                                    </div>
                                    <div className="bg-neutral-50 p-4 rounded-lg">
                                        <p className="text-sm text-neutral-500">Detection Accuracy</p>
                                        <p className="text-2xl font-bold">92%</p>
                                    </div>
                                    <div className="bg-neutral-50 p-4 rounded-lg">
                                        <p className="text-sm text-neutral-500">Cases per Officer</p>
                                        <p className="text-2xl font-bold">3.2</p>
                                    </div>
                                </div>
                            </Card>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
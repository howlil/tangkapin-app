import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { LuFileText, LuCalendar, LuMapPin, LuUsers } from 'react-icons/lu';
import useDashboardStore from '../../store/dashboardStore';

const CaseItem = ({ caseData, onDetails }) => {
    const statusColors = {
        'In Progress': 'bg-blue-100 text-blue-800',
        'Completed': 'bg-green-100 text-green-800',
        'Active': 'bg-yellow-100 text-yellow-800',
        'New': 'bg-red-100 text-red-800',
    };

    const statusColor = statusColors[caseData.status] || 'bg-neutral-100 text-neutral-800';

    return (
        <div className="mb-4 rounded-lg border border-neutral-200 bg-white overflow-hidden">
            <div className="p-5">
                <div className="flex items-center">
                    <div className="p-2 bg-neutral-100 rounded-md mr-4">
                        <LuFileText className="h-6 w-6 text-neutral-600" />
                    </div>

                    <div className="flex-1">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-medium">Case #{caseData.id}</h3>
                            <div className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor}`}>
                                {caseData.status}
                            </div>
                        </div>
                        <p className="text-neutral-700 mt-1">{caseData.title}</p>

                        <div className="flex flex-wrap mt-4 gap-4 text-sm text-neutral-500">
                            <div className="flex items-center">
                                <LuCalendar className="h-4 w-4 mr-1" />
                                <span>{caseData.date}</span>
                            </div>
                            <div className="flex items-center">
                                <LuMapPin className="h-4 w-4 mr-1" />
                                <span>{caseData.location}</span>
                            </div>
                            <div className="flex items-center">
                                <LuUsers className="h-4 w-4 mr-1" />
                                <span>{caseData.officersAssigned} Officers</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="border-t border-neutral-200 bg-neutral-50 py-3 px-5 text-right">
                <Button
                    onClick={() => onDetails(caseData.id)}
                    variant="secondary"
                    size="sm"
                >
                    Details
                </Button>
            </div>
        </div>
    );
};

const CaseManagement = () => {
    const { cases } = useDashboardStore();

    const handleViewDetails = (caseId) => {
        console.log(`View details for case ${caseId}`);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Case Management</CardTitle>
                <CardDescription>Track status and handling of cases</CardDescription>
            </CardHeader>
            <CardContent>
                {cases.map((caseItem) => (
                    <CaseItem
                        key={caseItem.id}
                        caseData={caseItem}
                        onDetails={handleViewDetails}
                    />
                ))}
            </CardContent>
        </Card>
    );
};

export default CaseManagement; 
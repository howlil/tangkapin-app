import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { LuFilter, LuMapPin } from 'react-icons/lu';
import useDashboardStore from '../../store/dashboardStore';

const OfficerCard = ({ officer, onAssign }) => {
    const statusColors = {
        'Standby': 'bg-yellow-100 text-yellow-800',
        'Available': 'bg-green-100 text-green-800',
        'On Duty': 'bg-blue-100 text-blue-800',
        'Unavailable': 'bg-red-100 text-red-800',
    };

    const statusColor = statusColors[officer.status] || 'bg-neutral-100 text-neutral-800';

    return (
        <div className="flex items-center p-4 border-b border-neutral-200 last:border-b-0">
            <div className="h-12 w-12 bg-green-500 rounded-full flex items-center justify-center text-white font-semibold mr-4">
                O
            </div>

            <div className="flex-1">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                        <h4 className="font-medium">Officer {officer.name}</h4>
                        <p className="text-sm text-neutral-500">{officer.unit}</p>
                    </div>

                    <div className="flex items-center mt-2 md:mt-0">
                        <div className={`px-3 py-1 rounded-full text-xs font-medium ${statusColor} mr-3`}>
                            {officer.status}
                        </div>

                        <Button
                            onClick={() => onAssign(officer.id)}
                            variant="outline"
                            size="sm"
                        >
                            Assign
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const OfficerAssignment = () => {
    const { officers, incidents } = useDashboardStore();

    const handleAssignOfficer = (officerId) => {
        // This would open a modal in a real app
        console.log(`Assign officer ${officerId} to incident`);
    };

    return (
        <Card className="h-full">
            <CardHeader className="flex flex-row justify-between items-center">
                <div>
                    <CardTitle>Available Officers</CardTitle>
                    <CardDescription>Officers ready for assignment</CardDescription>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                        <LuFilter className="h-4 w-4 mr-2" />
                        Filter
                    </Button>
                    <Button variant="outline" size="sm">
                        <LuMapPin className="h-4 w-4 mr-2" />
                        Center Map
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                <div className="divide-y divide-neutral-200">
                    {officers.map((officer) => (
                        <OfficerCard
                            key={officer.id}
                            officer={officer}
                            onAssign={handleAssignOfficer}
                        />
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};

export default OfficerAssignment; 
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { LuEye, LuMoreHorizontal } from 'react-icons/lu';
import useDashboardStore from '../../store/dashboardStore';

const StatusBadge = ({ status }) => {
    const variantMap = {
        'New': 'destructive',
        'Verified': 'secondary',
        'Assigned': 'secondary',
        'In Progress': 'warning',
        'Completed': 'success',
    };

    return (
        <Badge variant={variantMap[status] || 'default'}>
            {status}
        </Badge>
    );
};

const PriorityBadge = ({ priority }) => {
    const variantMap = {
        'High': 'destructive',
        'Medium': 'warning',
        'Low': 'success',
    };

    return (
        <Badge variant={variantMap[priority] || 'default'}>
            {priority}
        </Badge>
    );
};

const CrimeReportTable = () => {
    const { crimeReports } = useDashboardStore();
    const [currentPage, setCurrentPage] = useState(1);
    const [reportsPerPage] = useState(5);

    // Calculate pagination
    const indexOfLastReport = currentPage * reportsPerPage;
    const indexOfFirstReport = indexOfLastReport - reportsPerPage;
    const currentReports = crimeReports.slice(indexOfFirstReport, indexOfLastReport);

    const paginate = (pageNumber) => setCurrentPage(pageNumber);

    return (
        <Card className="h-full">
            <CardHeader className="flex flex-row justify-between items-center">
                <div>
                    <CardTitle>Crime Report Management</CardTitle>
                    <CardDescription>Manage all incoming crime reports</CardDescription>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                        Export
                    </Button>
                    <Button variant="default" size="sm">
                        Notifications
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                        <thead>
                            <tr className="border-b border-neutral-200">
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Report ID</th>
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Location</th>
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Time</th>
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Type</th>
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Priority</th>
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Status</th>
                                <th className="text-left px-4 py-3 text-sm font-medium text-neutral-500">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentReports.map((report) => (
                                <tr
                                    key={report.id}
                                    className="border-b border-neutral-200 hover:bg-neutral-50"
                                >
                                    <td className="px-4 py-4 text-sm">{report.id}</td>
                                    <td className="px-4 py-4 text-sm">{report.location}</td>
                                    <td className="px-4 py-4 text-sm">{report.time}</td>
                                    <td className="px-4 py-4 text-sm">{report.type}</td>
                                    <td className="px-4 py-4 text-sm">
                                        <PriorityBadge priority={report.priority} />
                                    </td>
                                    <td className="px-4 py-4 text-sm">
                                        <StatusBadge status={report.status} />
                                    </td>
                                    <td className="px-4 py-4 text-sm">
                                        <div className="flex items-center gap-2">
                                            <Button variant="ghost" size="icon" className="h-8 w-8">
                                                <LuEye className="h-4 w-4" />
                                            </Button>
                                            <Button variant="ghost" size="icon" className="h-8 w-8">
                                                <LuMoreHorizontal className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Simple Pagination */}
                <div className="flex justify-center mt-4">
                    <nav className="flex items-center gap-1">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => paginate(currentPage - 1)}
                            disabled={currentPage === 1}
                        >
                            Previous
                        </Button>

                        {Array.from({ length: Math.ceil(crimeReports.length / reportsPerPage) }).map((_, index) => (
                            <Button
                                key={index}
                                variant={currentPage === index + 1 ? "default" : "outline"}
                                size="sm"
                                onClick={() => paginate(index + 1)}
                                className="w-8"
                            >
                                {index + 1}
                            </Button>
                        ))}

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => paginate(currentPage + 1)}
                            disabled={currentPage === Math.ceil(crimeReports.length / reportsPerPage)}
                        >
                            Next
                        </Button>
                    </nav>
                </div>
            </CardContent>
        </Card>
    );
};

export default CrimeReportTable; 
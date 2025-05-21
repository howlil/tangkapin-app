import { create } from 'zustand';

const useDashboardStore = create((set) => ({
    // Dashboard summary stats
    stats: {
        newReports: 12,
        activeOfficers: 28,
        resolvedCases: 85,
        responseTime: 8.5,
    },

    // Incident data
    incidents: [
        { id: 1, type: 'Armed Robbery', location: '7-Eleven Main St. #123', status: 'Active', priority: 'High', time: '5 minutes ago', lat: 37.7749, lng: -122.4194 },
        { id: 2, type: 'Theft', location: 'Circle K Broadway #45', status: 'Verified', priority: 'Medium', time: '15 minutes ago', lat: 37.7849, lng: -122.4294 },
        { id: 3, type: 'Armed Robbery', location: 'QuickMart Central Ave #67', status: 'Officers Arrived', priority: 'High', time: '25 minutes ago', lat: 37.7949, lng: -122.4394 },
        { id: 4, type: 'Vandalism', location: 'MiniStop Oak St. #89', status: 'Closed', priority: 'Low', time: '1 hour ago', lat: 37.8049, lng: -122.4494 },
    ],

    // Officer data
    officers: [
        { id: 1, name: 'Michael Brown', status: 'Standby', unit: 'Criminal Investigation Unit', location: { lat: 37.7849, lng: -122.4294 } },
        { id: 2, name: 'Sarah Johnson', status: 'Available', unit: 'Patrol Unit', location: { lat: 37.7749, lng: -122.4394 } },
        { id: 3, name: 'David Chen', status: 'On Duty', unit: 'Traffic Unit', location: { lat: 37.7949, lng: -122.4294 } },
        { id: 4, name: 'Lisa Parker', status: 'Available', unit: 'Criminal Investigation Unit', location: { lat: 37.8049, lng: -122.4194 } },
    ],

    // Crime reports
    crimeReports: [
        { id: 'CR-2023-001', location: '7-Eleven Main St. #123', time: '05/12/2023 21:45', type: 'Armed Robbery', priority: 'High', status: 'New' },
        { id: 'CR-2023-002', location: 'Circle K Broadway #45', time: '05/12/2023 22:30', type: 'Theft', priority: 'Medium', status: 'Verified' },
        { id: 'CR-2023-003', location: 'QuickMart Central Ave #67', time: '05/13/2023 01:15', type: 'Armed Robbery', priority: 'High', status: 'Assigned' },
        { id: 'CR-2023-004', location: 'MiniStop Oak St. #89', time: '05/13/2023 03:20', type: 'Vandalism', priority: 'Low', status: 'Verified' },
        { id: 'CR-2023-005', location: '7-Eleven Park Ave #12', time: '05/13/2023 20:10', type: 'Theft', priority: 'Medium', status: 'New' },
        { id: 'CR-2023-006', location: 'Circle K River Rd #34', time: '05/14/2023 19:45', type: 'Armed Robbery', priority: 'High', status: 'New' },
    ],

    // Cases data
    cases: [
        { id: 1001, title: 'Armed Robbery at Circle K on Main St. #11', status: 'In Progress', date: '05/12/2023', location: 'South Jakarta', officersAssigned: 3 },
        { id: 1002, title: 'Armed Robbery at 7-Eleven on Main St. #12', status: 'Completed', date: '05/12/2023', location: 'South Jakarta', officersAssigned: 3 },
        { id: 1003, title: 'Armed Robbery at Circle K on Main St. #13', status: 'Active', date: '05/12/2023', location: 'South Jakarta', officersAssigned: 3 },
        { id: 1004, title: 'Armed Robbery at 7-Eleven on Main St. #14', status: 'In Progress', date: '05/12/2023', location: 'South Jakarta', officersAssigned: 3 },
        { id: 1005, title: 'Vandalism at MiniStop on Oak St.', status: 'Completed', date: '05/13/2023', location: 'South Jakarta', officersAssigned: 2 },
    ],

    // Analytics data
    analytics: {
        crimeStats: {
            averageIncidentsPerDay: 9.4,
            trend: '+12%',
        },
        performanceMetrics: {
            responseTime: '8.5 min',
            resolutionRate: '85%',
            detectionAccuracy: '92%',
            casesPerOfficer: 3.2,
        },
    },

    // Actions
    assignOfficerToIncident: (incidentId, officerId) =>
        set((state) => {
            // In a real app, this would make an API call
            console.log(`Assigning officer ${officerId} to incident ${incidentId}`);
            return state;
        }),

    updateIncidentStatus: (incidentId, newStatus) =>
        set((state) => {
            const updatedIncidents = state.incidents.map(incident =>
                incident.id === incidentId ? { ...incident, status: newStatus } : incident
            );
            return { incidents: updatedIncidents };
        }),

    addCrimeReport: (report) =>
        set((state) => ({
            crimeReports: [report, ...state.crimeReports]
        })),

    updateCaseStatus: (caseId, newStatus) =>
        set((state) => {
            const updatedCases = state.cases.map(caseItem =>
                caseItem.id === caseId ? { ...caseItem, status: newStatus } : caseItem
            );
            return { cases: updatedCases };
        }),
}));

export default useDashboardStore; 
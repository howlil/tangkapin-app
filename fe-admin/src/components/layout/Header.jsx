import { LuBell } from 'react-icons/lu';
import useDashboardStore from '../../store/dashboardStore';

const Header = () => {
    const { stats } = useDashboardStore();

    return (
        <header className="flex justify-between items-center p-6 border-b border-neutral-200 bg-white">
            <h1 className="text-2xl font-semibold text-neutral-900">Police Admin Dashboard</h1>

            <div className="flex items-center">
                <div className="relative mr-4">
                    <LuBell className="h-6 w-6 text-neutral-600" />
                    <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs flex items-center justify-center rounded-full">5</span>
                </div>

                <div className="flex items-center">
                    <div className="h-10 w-10 bg-green-500 rounded-full flex items-center justify-center text-white font-semibold">
                        C
                    </div>
                    <div className="ml-3">
                        <p className="text-sm font-medium text-neutral-900">Chief John Smith</p>
                        <p className="text-xs text-neutral-500">Police Admin</p>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header; 
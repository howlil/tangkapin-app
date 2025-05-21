import { Link } from 'react-router-dom';
import { LuLayoutDashboard, LuFileText, LuUsers, LuBriefcase, LuMap, LuBarChart, LuSettings, LuLogOut } from 'react-icons/lu';
import { cn } from '../../lib/utils';

const Sidebar = () => {
    const menuItems = [
        { icon: LuLayoutDashboard, label: 'Dashboard', path: '/' },
        { icon: LuFileText, label: 'Reports', path: '/reports' },
        { icon: LuUsers, label: 'Officers', path: '/officers' },
        { icon: LuBriefcase, label: 'Cases', path: '/cases' },
        { icon: LuMap, label: 'Map', path: '/map' },
        { icon: LuBarChart, label: 'Analytics', path: '/analytics' },
        { icon: LuSettings, label: 'Settings', path: '/settings' },
    ];

    const currentPath = window.location.pathname;

    return (
        <aside className="w-[250px] min-w-[250px] border-r border-neutral-200 bg-white h-screen flex flex-col">
            <div className="p-4 border-b border-neutral-200 flex items-center">
                <div className="h-10 w-10 bg-yellow-300 rounded-md flex items-center justify-center text-black font-bold">
                    T
                </div>
                <span className="ml-2 text-xl font-bold text-yellow-400">TangkapIn</span>
            </div>

            <nav className="flex-1 py-4">
                <ul className="space-y-1">
                    {menuItems.map((item) => (
                        <li key={item.path}>
                            <Link
                                to={item.path}
                                className={cn(
                                    "flex items-center px-4 py-3 mx-2 rounded-md text-neutral-600 hover:bg-neutral-100 transition-colors",
                                    currentPath === item.path && "bg-neutral-100 text-neutral-900 font-medium"
                                )}
                            >
                                <item.icon className="h-5 w-5 mr-3" />
                                <span>{item.label}</span>
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>

            <div className="p-4 border-t border-neutral-200">
                <Link to="/logout" className="flex items-center px-4 py-3 rounded-md text-neutral-600 hover:bg-neutral-100 transition-colors">
                    <LuLogOut className="h-5 w-5 mr-3" />
                    <span>Logout</span>
                </Link>
            </div>
        </aside>
    );
};

export default Sidebar; 
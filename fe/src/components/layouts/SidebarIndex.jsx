// src/components/SidebarIndex.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import logo from "../../assets/logo.png"
import {
  Home,
  FileStack,
  Cctv,
  LogOut,
} from 'lucide-react';

const SidebarIndex = () => {
  const navigation = [
    // { name: 'Home', path: '/dashboard', icon: Home },
    { name: 'Reports', path: '/reports?status=pending', icon: FileStack },
    // { name: 'CCTVs', path: '/cctvs', icon: Cctv },
  ];
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("name");
    window.location.href = "/login";
  };

  return (
    <div className="h-full flex flex-col">
      <div className='flex mt-6 justify-center items-center w-full'>

        <img className='w-40' src={logo} alt="s" />
      </div>
      <nav className="flex-1 px-2 mt-12 py-4 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center p-2 text-base font-medium rounded-md ${isActive
                ? 'bg-primer text-black'
                : 'text-gray-700 hover:bg-gray-200'
              }`
            }
          >
            <item.icon className="w-6 h-6 mr-3" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="px-2 py-4">
        <button
          onClick={handleLogout}
          className="flex items-center p-2 w-full text-left text-gray-700 hover:bg-gray-200 rounded-md">
          <LogOut className="w-6 h-6 mr-3" /> {/* Ikon logout */}
          Logout
        </button>
      </div>
    </div>
  );
};

export default SidebarIndex;

// src/components/NavSideMobile.js
import React, { useState } from 'react';
import { Menu, X } from 'lucide-react'; // Import ikon dari Lucide React
import SidebarIndex from './SidebarIndex';

const NavSideMobile = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <div className="flex items-center justify-between w-full">
        <h1 className="text-xl font-bold">MyApp</h1>
        <button
          onClick={toggleSidebar}
          className="p-2 text-gray-700 hover:text-gray-900 focus:outline-none"
          aria-label={isOpen ? 'Close menu' : 'Open menu'}
        >
          {isOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      </div>
      {/* Sidebar Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-40 flex">
          {/* Overlay */}
          <div
            className="fixed inset-0 bg-black opacity-50"
            onClick={toggleSidebar}
            aria-hidden="true"
          ></div>
          {/* Sidebar */}
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white shadow-xl">
            {/* Close Button */}
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:bg-gray-600"
                onClick={toggleSidebar}
                aria-label="Close sidebar"
              >
                <X className="h-6 w-6 text-white" />
              </button>
            </div>
            {/* Sidebar Content */}
            <SidebarIndex />
          </div>
          {/* Spacer */}
          <div className="flex-shrink-0 w-14"></div>
        </div>
      )}
    </>
  );
};

export default NavSideMobile;

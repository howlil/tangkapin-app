import React, { useState } from 'react';
import { Bell, User } from 'lucide-react'; 

const NavbarIndex = () => {

  const name = localStorage.getItem("name")


  return (
    <div className="flex items-center justify-end space-x-4">
      <div
        className="flex cursor-pointer items-center space-x-2"
      >
        <User className="w-6 h-6 text-gray-700" /> 
        <span className="text-gray-700 font-medium">{name || "John Doe"}</span>
      </div>

     
    </div>
  );
};

export default NavbarIndex;

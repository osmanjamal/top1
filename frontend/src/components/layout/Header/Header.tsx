import React from 'react';
import { Bell, User, ChevronDown } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="h-16 bg-[#1c2c4f] border-b border-gray-800">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center">
          <h2 className="text-lg font-medium">Dashboard</h2>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-[#2d4a7c]">
            <Bell className="w-5 h-5" />
          </button>

          {/* User menu */}
          <div className="relative">
            <button className="flex items-center space-x-3 p-2 text-gray-400 hover:text-white rounded-lg hover:bg-[#2d4a7c]">
              <User className="w-5 h-5" />
              <span>John Doe</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

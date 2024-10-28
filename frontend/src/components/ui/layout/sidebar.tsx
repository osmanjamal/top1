import React from 'react';
import { Home, BarChart2, Settings, User, Activity, Bell } from 'lucide-react';

interface SidebarProps {
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  return (
    <div className={`w-64 bg-[#1c2c4f] min-h-screen p-4 ${className}`}>
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white px-4">Trading Bot</h2>
      </div>
      
      <nav className="space-y-1">
        <NavItem icon={<Home />} label="Dashboard" active />
        <NavItem icon={<Activity />} label="Trading" />
        <NavItem icon={<BarChart2 />} label="Signals" />
        <NavItem icon={<Bell />} label="Notifications" />
        <NavItem icon={<User />} label="Profile" />
        <NavItem icon={<Settings />} label="Settings" />
      </nav>
      
      {/* User Profile Section */}
      <div className="absolute bottom-0 left-0 right-0 p-4">
        <div className="flex items-center space-x-3 px-4">
          <div className="w-8 h-8 bg-gray-700 rounded-full"></div>
          <div>
            <p className="text-sm font-medium text-white">John Doe</p>
            <p className="text-xs text-gray-400">Pro Trader</p>
          </div>
        </div>
      </div>
    </div>
  );
};

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
}

const NavItem: React.FC<NavItemProps> = ({ icon, label, active = false }) => (
  <button
    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
      ${active ? 'bg-[#2d4a7c] text-white' : 'text-gray-400 hover:bg-[#2d4a7c] hover:text-white'}`}
  >
    {icon}
    <span>{label}</span>
  </button>
);

export default Sidebar;
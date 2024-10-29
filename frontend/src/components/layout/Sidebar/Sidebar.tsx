import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Layout,
  LineChart,
  Bell,
  Settings,
  LogOut
} from 'lucide-react';

interface SidebarLink {
  icon: React.ReactNode;
  label: string;
  path: string;
}

const links: SidebarLink[] = [
  {
    icon: <Layout className="w-5 h-5" />,
    label: 'Dashboard',
    path: '/dashboard'
  },
  {
    icon: <LineChart className="w-5 h-5" />,
    label: 'Trading',
    path: '/trading'
  },
  {
    icon: <Bell className="w-5 h-5" />,
    label: 'Signals',
    path: '/signals'
  },
  {
    icon: <Settings className="w-5 h-5" />,
    label: 'Settings',
    path: '/settings'
  }
];

export const Sidebar: React.FC = () => {
  return (
    <div className="w-64 bg-[#1c2c4f] min-h-screen p-4 flex flex-col">
      {/* Logo */}
      <div className="mb-8 px-2">
        <h1 className="text-xl font-bold text-white">Trading Platform</h1>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1">
        <ul className="space-y-1">
          {links.map((link) => (
            <li key={link.path}>
              <NavLink
                to={link.path}
                className={({ isActive }) => `
                  flex items-center px-4 py-3 rounded-lg text-gray-300
                  hover:bg-[#2d4a7c] hover:text-white transition-colors
                  ${isActive ? 'bg-[#2d4a7c] text-white' : ''}
                `}
              >
                {link.icon}
                <span className="ml-3">{link.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout Button */}
      <button className="flex items-center px-4 py-3 text-gray-300 hover:text-white hover:bg-[#2d4a7c] rounded-lg w-full">
        <LogOut className="w-5 h-5" />
        <span className="ml-3">Logout</span>
      </button>
    </div>
  );
};

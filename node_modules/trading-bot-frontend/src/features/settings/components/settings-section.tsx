import React from 'react';
import { Shield, Bell, Globe, User, Key, DollarSign } from 'lucide-react';

interface SettingsTab {
  id: string;
  label: string;
  icon: React.ReactNode;
}

interface SettingsSidebarProps {
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export const SettingsSidebar: React.FC<SettingsSidebarProps> = ({
  activeTab,
  onTabChange
}) => {
  const tabs: SettingsTab[] = [
    { id: 'profile', label: 'Profile', icon: <User /> },
    { id: 'security', label: 'Security', icon: <Shield /> },
    { id: 'api', label: 'API Management', icon: <Key /> },
    { id: 'trading', label: 'Trading', icon: <DollarSign /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell /> },
    { id: 'preferences', label: 'Preferences', icon: <Globe /> },
  ];

  return (
    <div className="w-64 space-y-1">
      {tabs.map((tab) => (
        <SettingsTab
          key={tab.id}
          icon={tab.icon}
          label={tab.label}
          active={activeTab === tab.id}
          onClick={() => onTabChange(tab.id)}
        />
      ))}
    </div>
  );
};

interface SettingsTabProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}

const SettingsTab: React.FC<SettingsTabProps> = ({
  icon,
  label,
  active,
  onClick
}) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
      ${active ? 'bg-[#2d4a7c] text-white' : 'text-gray-400 hover:bg-[#2d4a7c] hover:text-white'}`}
  >
    {icon}
    <span>{label}</span>
  </button>
);

export default SettingsSidebar;
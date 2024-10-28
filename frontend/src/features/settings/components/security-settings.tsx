import React from 'react';
import { SettingsSection, SettingsRow } from './settings-section';

interface SecuritySettingsProps {
  onEnable2FA: () => void;
  onSetAntiPhishingCode: () => void;
}

export const SecuritySettings: React.FC<SecuritySettingsProps> = ({
  onEnable2FA,
  onSetAntiPhishingCode
}) => {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold mb-4 text-white">Security Settings</h2>

      {/* 2FA */}
      <SettingsSection title="Two-Factor Authentication">
        <SettingsRow
          title="2FA Authentication"
          description="Add an extra layer of security to your account"
        >
          <button 
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-white"
            onClick={onEnable2FA}
          >
            Enable 2FA
          </button>
        </SettingsRow>
      </SettingsSection>

      {/* Login Security */}
      <SettingsSection title="Login Security">
        <div className="space-y-4">
          <SettingsRow
            title="Email Confirmation"
            description="Require email confirmation for new devices"
          >
            <Switch />
          </SettingsRow>
          
          <SettingsRow
            title="Anti-Phishing Code"
            description="Add a code to verify official emails"
          >
            <button 
              className="px-4 py-2 bg-[#3d5a8c] hover:bg-[#4d6a9c] rounded-lg text-white"
              onClick={onSetAntiPhishingCode}
            >
              Set Code
            </button>
          </SettingsRow>
        </div>
      </SettingsSection>

      {/* Session Management */}
      <SettingsSection title="Active Sessions">
        <div className="space-y-4">
          <div className="p-4 bg-[#2d4a7c] rounded-lg">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="font-medium text-white">Current Session</h4>
                <p className="text-sm text-gray-400">Windows · Chrome · New York, US</p>
              </div>
              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs">
                Active
              </span>
            </div>
            <div className="text-sm text-gray-400">
              Last active: 2 minutes ago
            </div>
          </div>

          {/* Other Sessions */}
          <div className="p-4 bg-[#2d4a7c] rounded-lg">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="font-medium text-white">Mobile App</h4>
                <p className="text-sm text-gray-400">iOS · iPhone · London, UK</p>
              </div>
              <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs">
                Active
              </span>
            </div>
            <div className="text-sm text-gray-400">
              Last active: 1 hour ago
            </div>
          </div>
        </div>

        {/* Logout Options */}
        <div className="mt-4 flex space-x-4">
          <button className="px-4 py-2 border border-gray-700 rounded-lg text-white hover:bg-[#2d4a7c]">
            Logout Other Sessions
          </button>
          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white">
            Logout All Sessions
          </button>
        </div>
      </SettingsSection>

      {/* Password Security */}
      <SettingsSection 
        title="Password Security"
        description="Manage your account password and security settings"
      >
        <div className="space-y-4">
          <SettingsRow
            title="Password Age"
            description="Last changed 30 days ago"
          >
            <button className="px-4 py-2 bg-[#3d5a8c] hover:bg-[#4d6a9c] rounded-lg text-white">
              Change Password
            </button>
          </SettingsRow>

          <SettingsRow
            title="Password Requirements"
            description="Enforce strong password policy"
          >
            <Switch />
          </SettingsRow>
        </div>
      </SettingsSection>
    </div>
  );
};

// Switch Component
const Switch = () => (
  <div className="w-11 h-6 bg-emerald-600 rounded-full p-1 cursor-pointer">
    <div className="w-4 h-4 bg-white rounded-full ml-auto" />
  </div>
);

export default SecuritySettings;
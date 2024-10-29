import React from 'react';

interface SettingsSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const SettingsSection: React.FC<SettingsSectionProps> = ({
  title,
  description,
  children
}) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium mb-1 text-white">{title}</h3>
        {description && (
          <p className="text-sm text-gray-400">{description}</p>
        )}
      </div>
      {children}
    </div>
  );
};

interface SettingsRowProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const SettingsRow: React.FC<SettingsRowProps> = ({
  title,
  description,
  children
}) => {
  return (
    <div className="flex items-center justify-between p-4 bg-[#2d4a7c] rounded-lg">
      <div>
        <h4 className="font-medium text-white">{title}</h4>
        {description && (
          <p className="text-sm text-gray-400">{description}</p>
        )}
      </div>
      {children}
    </div>
  );
};

interface SettingsGroupProps {
  title: string;
  children: React.ReactNode;
}

export const SettingsGroup: React.FC<SettingsGroupProps> = ({
  title,
  children
}) => {
  return (
    <div className="bg-[#2d4a7c] rounded-lg p-4">
      <h4 className="font-medium mb-3 text-white">{title}</h4>
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};

export default {
  Section: SettingsSection,
  Row: SettingsRow,
  Group: SettingsGroup
};
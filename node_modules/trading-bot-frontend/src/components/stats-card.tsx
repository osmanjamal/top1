import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: string;
  positive?: boolean;
  icon?: React.ReactNode;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  positive = true,
  icon
}) => {
  return (
    <div className="bg-[#1c2c4f] rounded-lg p-4">
      <div className="flex items-center justify-between">
        {icon && (
          <div className="p-2 bg-[#2d4a7c] rounded-lg text-white">
            {icon}
          </div>
        )}
        {change && (
          <span className={`flex items-center text-sm ${
            positive ? 'text-green-500' : 'text-red-500'
          }`}>
            {change}
            {positive ? 
              <ArrowUpRight className="w-4 h-4 ml-1" /> : 
              <ArrowDownRight className="w-4 h-4 ml-1" />
            }
          </span>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-gray-400 text-sm">{title}</h3>
        <p className="text-2xl font-semibold text-white mt-1">{value}</p>
      </div>
    </div>
  );
};
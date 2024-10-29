import React from 'react';
import { ChevronDown } from 'lucide-react';

interface SignalsFilterProps {
  onFilterChange?: (filter: string) => void;
  onViewChange?: (view: 'bots' | 'signals') => void;
  currentView?: 'bots' | 'signals';
}

export const SignalsFilter: React.FC<SignalsFilterProps> = ({
  onFilterChange,
  onViewChange,
  currentView = 'bots'
}) => {
  return (
    <div className="border-b border-gray-800 p-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl text-white">List of signals</h1>
        
        <div className="flex items-center space-x-4">
          {/* Bot Filter Dropdown */}
          <div className="relative">
            <button 
              className="px-4 py-2 bg-[#1c2c4f] rounded flex items-center text-white"
              onClick={() => onFilterChange?.('all')}
            >
              All Bots
              <ChevronDown className="w-4 h-4 ml-2" />
            </button>
          </div>
          
          {/* View Toggle */}
          <div className="flex">
            <button 
              className={`px-6 py-2 ${
                currentView === 'bots' ? 'bg-[#1c2c4f]' : 'bg-transparent'
              } rounded-l text-white`}
              onClick={() => onViewChange?.('bots')}
            >
              Bots
            </button>
            <button 
              className={`px-6 py-2 ${
                currentView === 'signals' ? 'bg-[#1c2c4f]' : 'bg-transparent'
              } rounded-r text-white`}
              onClick={() => onViewChange?.('signals')}
            >
              Signals
            </button>
          </div>
        </div>
      </div>

      {/* Additional Filters */}
      <div className="mt-4 flex items-center space-x-4">
        <input
          type="text"
          placeholder="Search signals..."
          className="px-4 py-2 bg-[#1c2c4f] border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
        />
        
        <select className="px-4 py-2 bg-[#1c2c4f] border border-gray-700 rounded-lg text-white">
          <option value="24h">Last 24 hours</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="custom">Custom range</option>
        </select>
        
        <select className="px-4 py-2 bg-[#1c2c4f] border border-gray-700 rounded-lg text-white">
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="failed">Failed</option>
        </select>
      </div>
    </div>
  );
};

export default SignalsFilter;
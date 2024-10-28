import React from 'react';

interface BotCardProps {
  name: string;
  pair: string;
  status: 'active' | 'paused';
  signals: number;
  success: number;
  lastSignal: string;
  onViewDetails?: () => void;
}

export const BotCard: React.FC<BotCardProps> = ({
  name,
  pair,
  status,
  signals,
  success,
  lastSignal,
  onViewDetails
}) => {
  return (
    <div className="bg-[#1c2c4f] rounded-lg p-4">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-medium text-white">{name}</h3>
          <p className="text-sm text-gray-400">{pair}</p>
        </div>
        <span className={`
          px-2 py-1 rounded-full text-xs
          ${status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}
        `}>
          {status}
        </span>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <p className="text-gray-400">Signals Today</p>
          <p className="font-medium text-white">{signals}</p>
        </div>
        <div>
          <p className="text-gray-400">Success Rate</p>
          <p className="font-medium text-white">{success}%</p>
        </div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-400">Last Signal: {lastSignal}</span>
        <button 
          onClick={onViewDetails}
          className="text-emerald-500 hover:text-emerald-400"
        >
          View Details
        </button>
      </div>
    </div>
  );
};

interface BotCardGridProps {
  bots: BotCardProps[];
  onViewDetails: (botId: string) => void;
}

export const BotCardGrid: React.FC<BotCardGridProps> = ({
  bots,
  onViewDetails
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {bots.map((bot, index) => (
        <BotCard
          key={index}
          {...bot}
          onViewDetails={() => onViewDetails(bot.name)}
        />
      ))}
    </div>
  );
};

export default BotCardGrid;
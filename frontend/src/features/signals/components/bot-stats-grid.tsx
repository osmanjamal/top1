import React from 'react';
import { Activity, TrendingUp } from 'lucide-react';

interface BotStat {
  title: string;
  value: string | number;
  change: string;
  positive: boolean;
}

interface BotStatsGridProps {
  stats: BotStat[];
}

export const BotStatsGrid: React.FC<BotStatsGridProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      {stats.map((stat, index) => (
        <BotStatCard 
          key={index}
          title={stat.title}
          value={stat.value}
          change={stat.change}
          positive={stat.positive}
        />
      ))}
    </div>
  );
};

interface BotStatCardProps {
  title: string;
  value: string | number;
  change: string;
  positive: boolean;
}

const BotStatCard: React.FC<BotStatCardProps> = ({
  title,
  value,
  change,
  positive
}) => (
  <div className="bg-[#1c2c4f] rounded-lg p-4">
    <h3 className="text-gray-400 text-sm">{title}</h3>
    <div className="mt-2 flex items-baseline">
      <p className="text-2xl font-semibold text-white">{value}</p>
      <span className={`ml-2 text-sm ${positive ? 'text-green-500' : 'text-red-500'}`}>
        {change}
        {positive ? 
          <TrendingUp className="w-4 h-4 inline ml-1" /> : 
          <Activity className="w-4 h-4 inline ml-1" />
        }
      </span>
    </div>
  </div>
);

export default BotStatsGrid;
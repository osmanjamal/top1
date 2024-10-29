import React from 'react';
import { 
  Activity, 
  TrendingUp, 
  Settings, 
  Clock,
  DollarSign,
  AlertCircle,
  Pause,
  Play,
  RefreshCw
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BotDetailsProps {
  bot: {
    id: string;
    name: string;
    pair: string;
    status: 'active' | 'paused';
    statistics: {
      totalSignals: number;
      successRate: number;
      profitLoss: number;
      averageProfit: number;
      winningTrades: number;
      losingTrades: number;
    };
    settings: {
      leverage: number;
      positionSize: number;
      stopLoss: number;
      takeProfit: number;
    };
    performance: Array<{
      date: string;
      value: number;
    }>;
  };
  onPause: () => void;
  onResume: () => void;
  onReset: () => void;
  onSettingsChange: (settings: any) => void;
}

export const BotDetails: React.FC<BotDetailsProps> = ({
  bot,
  onPause,
  onResume,
  onReset,
  onSettingsChange
}) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-semibold text-white">{bot.name}</h2>
          <p className="text-gray-400">{bot.pair}</p>
        </div>
        <div className="flex items-center space-x-4">
          {bot.status === 'active' ? (
            <button 
              onClick={onPause}
              className="flex items-center px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30"
            >
              <Pause className="w-4 h-4 mr-2" />
              Pause Bot
            </button>
          ) : (
            <button 
              onClick={onResume}
              className="flex items-center px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30"
            >
              <Play className="w-4 h-4 mr-2" />
              Resume Bot
            </button>
          )}
          <button 
            onClick={onReset}
            className="p-2 text-gray-400 hover:text-white rounded-lg"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Signals"
          value={bot.statistics.totalSignals}
          icon={<Activity />}
          trend={`${bot.statistics.successRate}% Success`}
          positive
        />
        <StatCard
          title="Profit/Loss"
          value={`$${bot.statistics.profitLoss.toFixed(2)}`}
          icon={<DollarSign />}
          trend={`Avg. $${bot.statistics.averageProfit.toFixed(2)}`}
          positive={bot.statistics.profitLoss > 0}
        />
        <StatCard
          title="Win/Loss Ratio"
          value={`${bot.statistics.winningTrades}/${bot.statistics.losingTrades}`}
          icon={<TrendingUp />}
          trend="Last 24h"
          positive={bot.statistics.winningTrades > bot.statistics.losingTrades}
        />
      </div>

      {/* Performance Chart */}
      <div className="bg-[#1c2c4f] rounded-lg p-6">
        <h3 className="text-lg font-medium mb-4 text-white">Performance</h3>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={bot.performance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d4a7c" />
              <XAxis 
                dataKey="date" 
                stroke="#64748b"
                tickLine={false}
              />
              <YAxis 
                stroke="#64748b"
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1c2c4f',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bot Settings */}
      <div className="bg-[#1c2c4f] rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-white">Bot Settings</h3>
          <button className="text-emerald-500 hover:text-emerald-400">
            <Settings className="w-5 h-5" />
          </button>
        </div>
        <div className="grid grid-cols-2 gap-6">
          <SettingItem 
            label="Leverage"
            value={`${bot.settings.leverage}x`}
            info="Maximum leverage used for trades"
          />
          <SettingItem 
            label="Position Size"
            value={`$${bot.settings.positionSize}`}
            info="Size of each trade position"
          />
          <SettingItem 
            label="Stop Loss"
            value={`${bot.settings.stopLoss}%`}
            info="Automatic stop loss percentage"
          />
          <SettingItem 
            label="Take Profit"
            value={`${bot.settings.takeProfit}%`}
            info="Automatic take profit percentage"
          />
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend: string;
  positive: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  trend,
  positive
}) => (
  <div className="bg-[#1c2c4f] rounded-lg p-4">
    <div className="flex items-center justify-between">
      <div className="p-2 bg-[#2d4a7c] rounded-lg text-white">
        {icon}
      </div>
      <span className={`flex items-center text-sm ${
        positive ? 'text-green-500' : 'text-red-500'
      }`}>
        {trend}
      </span>
    </div>
    <div className="mt-4">
      <h3 className="text-gray-400 text-sm">{title}</h3>
      <p className="text-2xl font-semibold text-white mt-1">{value}</p>
    </div>
  </div>
);

interface SettingItemProps {
  label: string;
  value: string;
  info: string;
}

const SettingItem: React.FC<SettingItemProps> = ({ label, value, info }) => (
  <div className="bg-[#2d4a7c] p-4 rounded-lg">
    <div className="flex justify-between items-start mb-2">
      <h4 className="font-medium text-white">{label}</h4>
      <span className="text-emerald-500">{value}</span>
    </div>
    <p className="text-sm text-gray-400">{info}</p>
  </div>
);

export default BotDetails;
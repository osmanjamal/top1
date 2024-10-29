import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend 
} from 'recharts';
import { Settings, Maximize2, BarChart2, Minimize2 } from 'lucide-react';

interface TradingChartProps {
  data: Array<{
    time: string;
    price: number;
    volume: number;
  }>;
  symbol: string;
  onIntervalChange: (interval: string) => void;
  onFullscreen: () => void;
  isFullscreen: boolean;
}

const intervals = ['1m', '5m', '15m', '1h', '4h', '1d'];

export const TradingChart: React.FC<TradingChartProps> = ({
  data,
  symbol,
  onIntervalChange,
  onFullscreen,
  isFullscreen
}) => {
  return (
    <div className="bg-[#1c2c4f] rounded-lg p-4">
      {/* Chart Header */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-medium text-white">{symbol}</h2>
          <p className="text-sm text-gray-400">
            Last Price: ${data[data.length - 1]?.price.toFixed(2)}
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* Time Intervals */}
          <div className="flex bg-[#2d4a7c] rounded-lg">
            {intervals.map((interval) => (
              <button
                key={interval}
                onClick={() => onIntervalChange(interval)}
                className="px-3 py-1.5 text-sm hover:bg-[#3d5a8c] text-gray-300 first:rounded-l-lg last:rounded-r-lg"
              >
                {interval}
              </button>
            ))}
          </div>

          {/* Chart Controls */}
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-[#3d5a8c] rounded-lg text-gray-400 hover:text-white">
              <BarChart2 className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-[#3d5a8c] rounded-lg text-gray-400 hover:text-white">
              <Settings className="w-5 h-5" />
            </button>
            <button 
              onClick={onFullscreen} 
              className="p-2 hover:bg-[#3d5a8c] rounded-lg text-gray-400 hover:text-white"
            >
              {isFullscreen ? 
                <Minimize2 className="w-5 h-5" /> : 
                <Maximize2 className="w-5 h-5" />
              }
            </button>
          </div>
        </div>
      </div>

      {/* Main Chart */}
      <div className={`${isFullscreen ? 'h-[calc(100vh-200px)]' : 'h-[400px]'}`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#2d4a7c" 
              vertical={false}
            />
            <XAxis 
              dataKey="time" 
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              yAxisId="price"
              orientation="right"
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <YAxis 
              yAxisId="volume"
              orientation="left"
              stroke="#64748b"
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1c2c4f',
                border: 'none',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Legend />
            <Line 
              yAxisId="price"
              type="monotone" 
              dataKey="price" 
              stroke="#10b981" 
              strokeWidth={2}
              dot={false}
              name="Price"
            />
            <Line 
              yAxisId="volume"
              type="monotone" 
              dataKey="volume" 
              stroke="#60a5fa" 
              strokeWidth={2}
              dot={false}
              name="Volume"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Volume Analysis */}
      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-400">24h Volume</span>
          <p className="text-white font-medium">$1,234,567.89</p>
        </div>
        <div>
          <span className="text-gray-400">24h High</span>
          <p className="text-green-500 font-medium">$45,678.90</p>
        </div>
        <div>
          <span className="text-gray-400">24h Low</span>
          <p className="text-red-500 font-medium">$43,210.98</p>
        </div>
      </div>
    </div>
  );
};

export default TradingChart;
import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

interface DepthData {
  price: number;
  bids: number;
  asks: number;
}

interface MarketDepthChartProps {
  data: DepthData[];
  height?: number;
}

export const MarketDepthChart: React.FC<MarketDepthChartProps> = ({
  data,
  height = 300
}) => {
  return (
    <div className="w-full bg-[#1c2c4f] rounded-lg p-4">
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <XAxis 
            dataKey="price"
            type="number"
            tick={{ fill: '#9ca3af' }}
            axisLine={{ stroke: '#2d4a7c' }}
          />
          <YAxis
            tick={{ fill: '#9ca3af' }}
            axisLine={{ stroke: '#2d4a7c' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1c2c4f',
              border: '1px solid #2d4a7c',
              borderRadius: '8px'
            }}
            itemStyle={{ color: '#fff' }}
            labelStyle={{ color: '#9ca3af' }}
          />
          <Area
            type="monotone"
            dataKey="bids"
            stackId="1"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.2}
          />
          <Area
            type="monotone"
            dataKey="asks"
            stackId="2"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

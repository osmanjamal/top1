import React, { useMemo } from 'react';
import { ResponsiveContainer, Area, XAxis, YAxis, ComposedChart, Tooltip, CartesianGrid } from 'recharts';

interface CandleData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandlestickChartProps {
  data: CandleData[];
  width?: number;
  height?: number;
  onCrosshairMove?: (price: number | null) => void;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  data,
  width = '100%',
  height = 400,
  onCrosshairMove
}) => {
  // Transform data for visualization
  const chartData = useMemo(() => {
    return data.map(candle => ({
      ...candle,
      bullish: candle.close >= candle.open,
      color: candle.close >= candle.open ? '#22c55e' : '#ef4444',
      bodyHeight: Math.abs(candle.close - candle.open),
      wickHeight: candle.high - candle.low
    }));
  }, [data]);

  return (
    <div className="w-full bg-[#1c2c4f] rounded-lg p-4">
      <ResponsiveContainer width={width} height={height}>
        <ComposedChart
          data={chartData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          onMouseMove={(e) => {
            if (e.activePayload) {
              onCrosshairMove?.(e.activePayload[0].payload.close);
            }
          }}
          onMouseLeave={() => onCrosshairMove?.(null)}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="#2d4a7c" 
            vertical={false} 
          />
          
          <XAxis 
            dataKey="timestamp"
            tick={{ fill: '#9ca3af' }}
            axisLine={{ stroke: '#2d4a7c' }}
          />
          
          <YAxis 
            yAxisId="price"
            orientation="right"
            domain={['dataMin', 'dataMax']}
            tick={{ fill: '#9ca3af' }}
            axisLine={{ stroke: '#2d4a7c' }}
          />
          
          <YAxis 
            yAxisId="volume"
            orientation="left"
            domain={['dataMin', 'dataMax']}
            tick={{ fill: '#9ca3af' }}
            axisLine={{ stroke: '#2d4a7c' }}
          />
          
          <Tooltip
            contentStyle={{
              backgroundColor: '#1c2c4f',
              border: '1px solid #2d4a7c',
              borderRadius: '8px',
              padding: '10px'
            }}
            labelStyle={{ color: '#9ca3af' }}
            itemStyle={{ color: '#fff' }}
            formatter={(value: any, name: string) => [
              `$${Number(value).toLocaleString()}`,
              name.charAt(0).toUpperCase() + name.slice(1)
            ]}
          />

          {/* Volume Area */}
          <Area
            yAxisId="volume"
            dataKey="volume"
            fill="#3b82f6"
            stroke="#3b82f6"
            fillOpacity={0.2}
          />

          {/* Custom Candles */}
          {chartData.map((candle, index) => (
            <g key={index}>
              {/* Wick */}
              <line
                x1={index + 0.5}
                y1={candle.high}
                x2={index + 0.5}
                y2={candle.low}
                stroke={candle.color}
                strokeWidth={1}
              />
              {/* Body */}
              <rect
                x={index + 0.3}
                y={candle.bullish ? candle.close : candle.open}
                width={0.4}
                height={candle.bodyHeight}
                fill={candle.color}
              />
            </g>
          ))}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

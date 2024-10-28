import React from 'react';
import { Info } from 'lucide-react';

interface SignalData {
  bot: {
    name: string;
    icon: string;
    exchange: string;
    leverage: string;
  };
  signal: 'Buy' | 'Sell';
  triggerTime: {
    time: string;
    date: string;
  };
  triggerPrice: string;
  signalStatus: string;
  price: string;
  size: {
    btc: string;
    usdt: string;
  };
  orderStatus: string;
  orderTime: {
    time: string;
    date: string;
  };
}

interface SignalsTableProps {
  signals: SignalData[];
}

export const SignalsTable: React.FC<SignalsTableProps> = ({ signals }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="text-left text-gray-400 text-sm">
            <th className="p-4">Bot</th>
            <th className="p-4">Signal</th>
            <th className="p-4">Trigger time</th>
            <th className="p-4">Trigger price</th>
            <th className="p-4">Signal status</th>
            <th className="p-4">Price</th>
            <th className="p-4">Size</th>
            <th className="p-4">Order status</th>
            <th className="p-4">Order time</th>
          </tr>
        </thead>
        <tbody className="text-sm">
          {signals.map((signal, index) => (
            <SignalRow key={index} {...signal} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

const SignalRow: React.FC<SignalData> = ({
  bot,
  signal,
  triggerTime,
  triggerPrice,
  signalStatus,
  price,
  size,
  orderStatus,
  orderTime
}) => (
  <tr className="border-t border-gray-800 hover:bg-[#1c2c4f]">
    <td className="p-4">
      <div className="flex items-center space-x-2">
        <span>{bot.icon}</span>
        <span>{bot.name}</span>
        <div className="flex items-center space-x-1">
          <img src="/exchange-icon.png" className="w-4 h-4" alt="Exchange" />
          <span className="bg-amber-500/30 text-amber-500 px-1 rounded text-xs">
            {bot.leverage}
          </span>
          <Info className="w-4 h-4 text-gray-500" />
        </div>
      </div>
    </td>
    <td className="p-4">
      <span className={`px-2 py-1 rounded ${
        signal === 'Buy' 
          ? 'bg-green-500/20 text-green-400' 
          : 'bg-red-500/20 text-red-400'
      }`}>
        {signal}
      </span>
    </td>
    <td className="p-4">
      <div>
        <div>{triggerTime.time}</div>
        <div className="text-gray-500">{triggerTime.date}</div>
      </div>
    </td>
    <td className="p-4">{triggerPrice}</td>
    <td className="p-4">
      <span className="text-teal-400">{signalStatus}</span>
    </td>
    <td className="p-4">{price}</td>
    <td className="p-4">
      <div>
        <div>{size.btc}</div>
        <div className="text-gray-500">{size.usdt}</div>
      </div>
    </td>
    <td className="p-4">
      <span className="text-teal-400">{orderStatus}</span>
    </td>
    <td className="p-4">
      <div>
        <div>{orderTime.time}</div>
        <div className="text-gray-500">{orderTime.date}</div>
      </div>
    </td>
  </tr>
);

export default SignalsTable;
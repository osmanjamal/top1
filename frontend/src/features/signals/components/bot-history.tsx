import React from 'react';
import { ArrowUpRight, ArrowDownRight, Calendar, Clock } from 'lucide-react';

interface TradeHistory {
  id: string;
  type: 'buy' | 'sell';
  pair: string;
  entryPrice: number;
  exitPrice: number;
  profit: number;
  date: string;
  time: string;
  size: {
    amount: string;
    value: string;
  };
  status: 'completed' | 'cancelled' | 'failed';
}

interface BotHistoryProps {
  trades: TradeHistory[];
}

export const BotHistory: React.FC<BotHistoryProps> = ({ trades }) => {
  return (
    <div className="bg-[#1c2c4f] rounded-lg p-6">
      <h3 className="text-lg font-medium mb-6 text-white">Trading History</h3>

      <div className="space-y-4">
        {trades.map((trade) => (
          <TradeHistoryCard key={trade.id} trade={trade} />
        ))}
      </div>
    </div>
  );
};

interface TradeHistoryCardProps {
  trade: TradeHistory;
}

const TradeHistoryCard: React.FC<TradeHistoryCardProps> = ({ trade }) => {
  const isProfitable = trade.profit > 0;
  
  return (
    <div className="p-4 bg-[#2d4a7c] rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className={`
            w-10 h-10 rounded-lg flex items-center justify-center
            ${trade.type === 'buy' 
              ? 'bg-green-500/20 text-green-500' 
              : 'bg-red-500/20 text-red-500'
            }
          `}>
            {trade.type === 'buy' 
              ? <ArrowUpRight className="w-5 h-5" />
              : <ArrowDownRight className="w-5 h-5" />
            }
          </div>
          
          <div>
            <h4 className="font-medium text-white">
              {trade.type === 'buy' ? 'Long' : 'Short'} {trade.pair}
            </h4>
            <div className="flex items-center text-sm text-gray-400 mt-1">
              <Calendar className="w-4 h-4 mr-1" />
              <span>{trade.date}</span>
              <Clock className="w-4 h-4 ml-3 mr-1" />
              <span>{trade.time}</span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <span className={`text-lg font-medium ${
            isProfitable ? 'text-green-500' : 'text-red-500'
          }`}>
            {isProfitable ? '+' : ''}{trade.profit}%
          </span>
          <div className="text-sm text-gray-400 mt-1">
            {trade.size.amount} ({trade.size.value})
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-400">Entry Price</span>
          <p className="text-white">${trade.entryPrice}</p>
        </div>
        <div>
          <span className="text-gray-400">Exit Price</span>
          <p className="text-white">${trade.exitPrice}</p>
        </div>
      </div>

      {/* Status Badge */}
      <div className="mt-4 flex justify-end">
        <span className={`
          px-3 py-1 rounded-full text-xs
          ${trade.status === 'completed' ? 'bg-green-500/20 text-green-400' :
            trade.status === 'cancelled' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-red-500/20 text-red-400'}
        `}>
          {trade.status}
        </span>
      </div>
    </div>
  );
};

export default BotHistory;
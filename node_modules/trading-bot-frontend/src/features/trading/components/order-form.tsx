import React, { useState } from 'react';

interface OrderFormProps {
  symbol: string;
  balance: {
    asset: number;
    quote: number;
  };
  lastPrice: number;
  onSubmitOrder: (order: OrderData) => void;
}

interface OrderData {
  type: 'market' | 'limit';
  side: 'buy' | 'sell';
  price: number;
  amount: number;
  total: number;
  leverage: number;
  stopLoss?: number;
  takeProfit?: number;
}

export const OrderForm: React.FC<OrderFormProps> = ({
  symbol,
  balance,
  lastPrice,
  onSubmitOrder
}) => {
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [leverage, setLeverage] = useState(1);
  const [advancedMode, setAdvancedMode] = useState(false);

  const [formData, setFormData] = useState<OrderData>({
    type: 'market',
    side: 'buy',
    price: lastPrice,
    amount: 0,
    total: 0,
    leverage: 1
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmitOrder(formData);
  };

  return (
    <div className="bg-[#1c2c4f] rounded-lg p-4">
      <div className="flex justify-between items-center mb-6">
        <div className="flex space-x-2">
          {/* Market/Limit Toggle */}
          <button
            onClick={() => setOrderType('market')}
            className={`px-4 py-2 rounded-lg ${
              orderType === 'market'
                ? 'bg-emerald-600 text-white'
                : 'bg-[#2d4a7c] text-gray-400 hover:text-white'
            }`}
          >
            Market
          </button>
          <button
            onClick={() => setOrderType('limit')}
            className={`px-4 py-2 rounded-lg ${
              orderType === 'limit'
                ? 'bg-emerald-600 text-white'
                : 'bg-[#2d4a7c] text-gray-400 hover:text-white'
            }`}
          >
            Limit
          </button>
        </div>

        {/* Advanced Mode Toggle */}
        <button
          onClick={() => setAdvancedMode(!advancedMode)}
          className="text-sm text-emerald-500 hover:text-emerald-400"
        >
          {advancedMode ? 'Simple Mode' : 'Advanced Mode'}
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Buy/Sell Tabs */}
        <div className="grid grid-cols-2 gap-2 mb-6">
          <button
            type="button"
            onClick={() => setOrderSide('buy')}
            className={`py-3 rounded-lg font-medium ${
              orderSide === 'buy'
                ? 'bg-green-600 text-white'
                : 'bg-[#2d4a7c] text-gray-400 hover:text-white'
            }`}
          >
            Buy
          </button>
          <button
            type="button"
            onClick={() => setOrderSide('sell')}
            className={`py-3 rounded-lg font-medium ${
              orderSide === 'sell'
                ? 'bg-red-600 text-white'
                : 'bg-[#2d4a7c] text-gray-400 hover:text-white'
            }`}
          >
            Sell
          </button>
        </div>

        {/* Order Inputs */}
        <div className="space-y-4">
          {/* Price Input - Only for Limit Orders */}
          {orderType === 'limit' && (
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Price
              </label>
              <div className="relative">
                <input
                  type="number"
                  className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-3 text-white"
                  value={formData.price}
                  onChange={(e) => setFormData({...formData, price: Number(e.target.value)})}
                />
                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                  USDT
                </span>
              </div>
            </div>
          )}

          {/* Amount Input */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Amount
            </label>
            <div className="relative">
              <input
                type="number"
                className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-3 text-white"
                value={formData.amount}
                onChange={(e) => setFormData({...formData, amount: Number(e.target.value)})}
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                BTC
              </span>
            </div>
            {/* Percentage Buttons */}
            <div className="flex justify-between mt-2">
              {[25, 50, 75, 100].map((percent) => (
                <button
                  key={percent}
                  type="button"
                  className="px-3 py-1 bg-[#2d4a7c] hover:bg-[#3d5a8c] rounded text-sm text-gray-400 hover:text-white"
                  onClick={() => {
                    // Calculate amount based on balance percentage
                  }}
                >
                  {percent}%
                </button>
              ))}
            </div>
          </div>

          {/* Leverage Slider (Advanced Mode) */}
          {advancedMode && (
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Leverage: {leverage}x
              </label>
              <input
                type="range"
                min="1"
                max="100"
                value={leverage}
                onChange={(e) => setLeverage(Number(e.target.value))}
                className="w-full"
              />
            </div>
          )}

          {/* Stop Loss & Take Profit (Advanced Mode) */}
          {advancedMode && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Stop Loss
                </label>
                <input
                  type="number"
                  className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-3 text-white"
                  placeholder="Optional"
                  onChange={(e) => setFormData({...formData, stopLoss: Number(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Take Profit
                </label>
                <input
                  type="number"
                  className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-3 text-white"
                  placeholder="Optional"
                  onChange={(e) => setFormData({...formData, takeProfit: Number(e.target.value)})}
                />
              </div>
            </div>
          )}

          {/* Order Button */}
          <button
            type="submit"
            className={`w-full py-4 rounded-lg font-medium ${
              orderSide === 'buy'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
            } text-white`}
          >
            {orderSide === 'buy' ? 'Buy' : 'Sell'} {symbol}
          </button>
        </div>

        {/* Available Balance */}
        <div className="text-sm text-gray-400">
          Available: {balance.quote.toFixed(2)} USDT
        </div>
      </form>
    </div>
  );
};

export default OrderForm;
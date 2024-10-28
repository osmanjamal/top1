import React, { useState } from 'react';
import { Copy } from 'lucide-react';

interface CreateBotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateBot: (botConfig: any) => void;
}

export const CreateBotModal: React.FC<CreateBotModalProps> = ({
  isOpen,
  onClose,
  onCreateBot
}) => {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState({
    pair: 'BTCUSDT',
    leverage: '10',
    size: '100'
  });

  if (!isOpen) return null;

  const handleCreate = () => {
    onCreateBot(config);
    onClose();
    setStep(1);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-[#1c2c4f] rounded-lg w-full max-w-2xl p-6">
        {/* Modal Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-white">Create Signal Bot</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {/* Steps Indicator */}
        <div className="flex justify-between mb-8">
          {[1, 2, 3].map((currentStep) => (
            <div 
              key={currentStep}
              className={`flex items-center ${currentStep < 3 ? 'flex-1' : ''}`}
            >
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center
                ${currentStep <= step ? 'bg-emerald-600' : 'bg-gray-700'}
              `}>
                {currentStep}
              </div>
              {currentStep < 3 && (
                <div className={`
                  flex-1 h-1 mx-2
                  ${currentStep < step ? 'bg-emerald-600' : 'bg-gray-700'}
                `} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="space-y-6">
          {step === 1 && (
            <>
              <div>
                <h3 className="text-lg mb-4 text-white">Set Webhook URL</h3>
                <div className="bg-[#2d4a7c] p-4 rounded-lg flex items-center">
                  <code className="flex-1 text-white">
                    https://api.yourbot.com/webhook/signals
                  </code>
                  <button className="ml-2 text-emerald-500 hover:text-emerald-400">
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <button 
                onClick={() => setStep(2)}
                className="w-full bg-emerald-600 hover:bg-emerald-700 py-2 rounded-lg text-white"
              >
                Continue
              </button>
            </>
          )}

          {step === 2 && (
            <>
              <div>
                <h3 className="text-lg mb-4 text-white">General Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm mb-2 text-white">Trading Pair</label>
                    <select 
                      className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-2 text-white"
                      value={config.pair}
                      onChange={(e) => setConfig({...config, pair: e.target.value})}
                    >
                      <option>BTCUSDT</option>
                      <option>ETHUSDT</option>
                      <option>DOGEUSDT</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm mb-2 text-white">Leverage</label>
                    <select 
                      className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-2 text-white"
                      value={config.leverage}
                      onChange={(e) => setConfig({...config, leverage: e.target.value})}
                    >
                      <option>1x</option>
                      <option>5x</option>
                      <option>10x</option>
                      <option>20x</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm mb-2 text-white">Position Size (USDT)</label>
                    <input 
                      type="number"
                      className="w-full bg-[#2d4a7c] border border-gray-700 rounded-lg px-4 py-2 text-white"
                      placeholder="100"
                      value={config.size}
                      onChange={(e) => setConfig({...config, size: e.target.value})}
                    />
                  </div>
                </div>
              </div>
              <div className="flex space-x-4">
                <button 
                  onClick={() => setStep(1)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 py-2 rounded-lg text-white"
                >
                  Back
                </button>
                <button 
                  onClick={() => setStep(3)}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 py-2 rounded-lg text-white"
                >
                  Continue
                </button>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <div>
                <h3 className="text-lg mb-4 text-white">Strategy Configuration</h3>
                <div className="bg-[#2d4a7c] p-4 rounded-lg">
                  <pre className="text-sm overflow-auto text-white">
                    {JSON.stringify({
                      webhook: {
                        url: "https://api.yourbot.com/webhook/signals",
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json"
                        }
                      },
                      strategy: config
                    }, null, 2)}
                  </pre>
                </div>
              </div>
              <div className="flex space-x-4">
                <button 
                  onClick={() => setStep(2)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 py-2 rounded-lg text-white"
                >
                  Back
                </button>
                <button 
                  onClick={handleCreate}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700 py-2 rounded-lg text-white"
                >
                  Create Bot
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateBotModal;
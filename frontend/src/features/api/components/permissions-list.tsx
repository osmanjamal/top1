import React from 'react';
import { Shield } from 'lucide-react';

export const SecurityNotice = () => {
  return (
    <div className="bg-[#2d4a7c] rounded-lg p-4 mb-8 flex items-start space-x-4">
      <Shield className="w-6 h-6 text-emerald-500 flex-shrink-0" />
      <div>
        <h3 className="font-medium mb-1 text-white">Your Security is Our Priority</h3>
        <p className="text-gray-400 text-sm">
          All API keys are encrypted and stored securely. We never have access to your funds.
        </p>
      </div>
    </div>
  );
};

export default SecurityNotice;
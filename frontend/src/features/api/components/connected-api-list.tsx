import React from 'react';
import { Key, AlertCircle } from 'lucide-react';

interface ConnectedAPI {
  id: string;
  exchange: string;
  name: string;
  lastUsed: string;
  status: 'active' | 'update_required';
}

interface ConnectedAPIListProps {
  apis: ConnectedAPI[];
  onViewDetails: (apiId: string) => void;
}

export const ConnectedAPIList: React.FC<ConnectedAPIListProps> = ({
  apis,
  onViewDetails
}) => {
  return (
    <div className="bg-[#1c2c4f] rounded-lg p-6">
      <h3 className="text-lg font-medium mb-4 text-white">Connected APIs</h3>
      
      <div className="space-y-4">
        {apis.map((api) => (
          <ConnectedAPICard 
            key={api.id}
            {...api}
            onViewDetails={() => onViewDetails(api.id)}
          />
        ))}
      </div>
    </div>
  );
};

interface ConnectedAPICardProps extends ConnectedAPI {
  onViewDetails: () => void;
}

const ConnectedAPICard: React.FC<ConnectedAPICardProps> = ({
  exchange,
  name,
  lastUsed,
  status,
  onViewDetails
}) => (
  <div className="flex items-center justify-between p-4 bg-[#2d4a7c] rounded-lg">
    <div className="flex items-center space-x-4">
      <Key className="w-5 h-5 text-gray-400" />
      <div>
        <h4 className="font-medium text-white">{exchange}</h4>
        <p className="text-sm text-gray-400">Last used: {lastUsed}</p>
      </div>
    </div>
    <div className="flex items-center space-x-4">
      <span className={`px-3 py-1 rounded-full text-xs ${
        status === 'active' 
          ? 'bg-green-500/20 text-green-400' 
          : 'bg-yellow-500/20 text-yellow-400'
      }`}>
        {status === 'active' ? 'Active' : 'Update Required'}
      </span>
      <button 
        className="p-2 hover:bg-[#3d5a8c] rounded-lg"
        onClick={onViewDetails}
      >
        <AlertCircle className="w-5 h-5 text-gray-400" />
      </button>
    </div>
  </div>
);

export default ConnectedAPIList;
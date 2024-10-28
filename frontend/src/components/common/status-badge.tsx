import React from 'react';

type StatusType = 'success' | 'warning' | 'error' | 'info' | 'pending';

interface StatusBadgeProps {
  status: StatusType;
  text: string;
  className?: string;
}

const statusStyles = {
  success: 'bg-green-500/20 text-green-400',
  warning: 'bg-yellow-500/20 text-yellow-400',
  error: 'bg-red-500/20 text-red-400',
  info: 'bg-blue-500/20 text-blue-400',
  pending: 'bg-gray-500/20 text-gray-400'
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  text,
  className = ''
}) => {
  return (
    <span className={`
      inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
      ${statusStyles[status]}
      ${className}
    `}>
      {/* Optional Status Dot */}
      <span className={`
        w-1.5 h-1.5 rounded-full mr-1.5
        ${status === 'success' && 'bg-green-400'}
        ${status === 'warning' && 'bg-yellow-400'}
        ${status === 'error' && 'bg-red-400'}
        ${status === 'info' && 'bg-blue-400'}
        ${status === 'pending' && 'bg-gray-400'}
      `} />
      {text}
    </span>
  );
};

export default StatusBadge;
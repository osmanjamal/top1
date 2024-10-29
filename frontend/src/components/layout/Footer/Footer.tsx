import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="h-16 bg-[#1c2c4f] border-t border-gray-800">
      <div className="h-full px-4 flex items-center justify-between text-sm text-gray-400">
        <div>© 2024 Trading Platform. All rights reserved.</div>
        <div className="flex space-x-4">
          <a href="#" className="hover:text-white">Terms</a>
          <a href="#" className="hover:text-white">Privacy</a>
          <a href="#" className="hover:text-white">Contact</a>
        </div>
      </div>
    </footer>
  );
};

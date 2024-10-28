import React from 'react';
import Navbar from './navbar';
import Sidebar from './sidebar';

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

const PageContainer: React.FC<PageContainerProps> = ({ children, className = '' }) => {
  return (
    <div className="min-h-screen bg-[#1a1f2e] text-white">
      <Navbar />
      
      <div className="flex">
        <Sidebar />
        
        {/* Main Content */}
        <main className={`flex-1 pt-16 pl-64 ${className}`}>
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default PageContainer;
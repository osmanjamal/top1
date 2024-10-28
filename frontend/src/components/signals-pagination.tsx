import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onPerPageChange: (perPage: number) => void;
  perPage: number;
}

export const SignalsPagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  onPerPageChange,
  perPage
}) => {
  return (
    <div className="p-4 flex items-center justify-between">
      {/* Per Page Selector */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-400">Show:</span>
        <select 
          className="bg-[#1c2c4f] rounded px-3 py-2 text-white border border-gray-700"
          value={perPage}
          onChange={(e) => onPerPageChange(Number(e.target.value))}
        >
          <option value={10}>10</option>
          <option value={25}>25</option>
          <option value={50}>50</option>
        </select>
      </div>

      {/* Page Numbers */}
      <div className="flex items-center space-x-2">
        <PaginationButton
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </PaginationButton>

        <div className="flex items-center space-x-1">
          {/* Render page numbers */}
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`px-3 py-1 rounded ${
                currentPage === page
                  ? 'bg-teal-500 text-white'
                  : 'text-gray-400 hover:bg-[#2d4a7c]'
              }`}
            >
              {page}
            </button>
          ))}
        </div>

        <PaginationButton
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </PaginationButton>
      </div>

      {/* Total Results */}
      <div className="text-sm text-gray-400">
        Showing {(currentPage - 1) * perPage + 1} to {Math.min(currentPage * perPage, totalPages * perPage)} of {totalPages * perPage} results
      </div>
    </div>
  );
};

interface PaginationButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}

const PaginationButton: React.FC<PaginationButtonProps> = ({
  children,
  onClick,
  disabled = false
}) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`px-4 py-2 rounded ${
      disabled
        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
        : 'bg-[#1c2c4f] text-white hover:bg-[#2d4a7c]'
    }`}
  >
    {children}
  </button>
);

export default SignalsPagination;
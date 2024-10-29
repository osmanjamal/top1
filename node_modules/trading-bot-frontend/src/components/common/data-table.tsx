import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from 'lucide-react';

interface Column {
  key: string;
  title: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataTableProps {
  columns: Column[];
  data: any[];
  className?: string;
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    pageSize: number;
    onPageSizeChange?: (size: number) => void;
  };
}

export const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  className = '',
  onSort,
  pagination
}) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    
    if (sortConfig?.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }

    setSortConfig({ key, direction });
    onSort?.(key, direction);
  };

  const renderSortIcon = (column: Column) => {
    if (!column.sortable) return null;

    if (sortConfig?.key === column.key) {
      return sortConfig.direction === 'asc' ? 
        <ChevronUp className="w-4 h-4" /> : 
        <ChevronDown className="w-4 h-4" />;
    }

    return <ChevronDown className="w-4 h-4 opacity-0 group-hover:opacity-100" />;
  };

  return (
    <div className={`bg-[#1c2c4f] rounded-lg ${className}`}>
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-800">
              {columns.map((column) => (
                <th 
                  key={column.key}
                  className={`
                    px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider
                    ${column.sortable ? 'cursor-pointer group' : ''}
                  `}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.title}</span>
                    {renderSortIcon(column)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {data.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className="hover:bg-[#2d4a7c] transition-colors"
              >
                {columns.map((column) => (
                  <td 
                    key={column.key} 
                    className="px-6 py-4 text-sm text-white"
                  >
                    {column.render ? 
                      column.render(row[column.key], row) : 
                      row[column.key]
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="px-6 py-4 flex items-center justify-between border-t border-gray-800">
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>Show</span>
            <select 
              className="bg-[#2d4a7c] border border-gray-700 rounded px-2 py-1 text-white"
              value={pagination.pageSize}
              onChange={(e) => pagination.onPageSizeChange?.(Number(e.target.value))}
            >
              {[10, 20, 30, 50].map((size) => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
            <span>entries</span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage === 1}
              className={`
                p-2 rounded-lg
                ${pagination.currentPage === 1 
                  ? 'text-gray-600 cursor-not-allowed' 
                  : 'text-gray-400 hover:bg-[#2d4a7c] hover:text-white'}
              `}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-1">
              {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => pagination.onPageChange(page)}
                  className={`
                    px-3 py-1 rounded-lg text-sm
                    ${pagination.currentPage === page 
                      ? 'bg-emerald-600 text-white' 
                      : 'text-gray-400 hover:bg-[#2d4a7c] hover:text-white'}
                  `}
                >
                  {page}
                </button>
              ))}
            </div>

            <button
              onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage === pagination.totalPages}
              className={`
                p-2 rounded-lg
                ${pagination.currentPage === pagination.totalPages 
                  ? 'text-gray-600 cursor-not-allowed' 
                  : 'text-gray-400 hover:bg-[#2d4a7c] hover:text-white'}
              `}
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
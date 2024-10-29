import React from 'react';

interface Column<T> {
  key: string;
  title: string;
  render?: (value: any, row: T) => React.ReactNode;
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
}

export function Table<T extends { id?: string | number }>({
  data,
  columns,
  loading,
  onRowClick
}: TableProps<T>) {
  if (loading) {
    return (
      <div className="w-full bg-[#1c2c4f] rounded-lg p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-[#2d4a7c] rounded w-full"/>
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-[#2d4a7c] rounded w-full"/>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="text-left text-gray-400 text-sm border-b border-gray-800">
            {columns.map((column) => (
              <th key={column.key} className="p-4 font-medium">
                {column.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr
              key={row.id || index}
              onClick={() => onRowClick?.(row)}
              className={`
                border-b border-gray-800 text-sm
                ${onRowClick ? 'cursor-pointer hover:bg-[#2d4a7c]' : ''}
              `}
            >
              {columns.map((column) => (
                <td key={column.key} className="p-4">
                  {column.render
                    ? column.render(row[column.key as keyof T], row)
                    : String(row[column.key as keyof T])
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


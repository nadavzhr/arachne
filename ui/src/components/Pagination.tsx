import React from 'react';

interface PaginationProps {
  currentPage: number;
  setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
  totalPages: number;
  itemsPerPage: number;
  filteredJobsCount: number;
}

export const Pagination = ({
  currentPage,
  setCurrentPage,
  totalPages,
  itemsPerPage,
  filteredJobsCount,
}: PaginationProps) => {
  const startIndex = filteredJobsCount === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
  const endIndex = Math.min(currentPage * itemsPerPage, filteredJobsCount);

  return (
    <div className="h-14 border-t border-arachne-border flex items-center justify-between px-4 md:px-8 bg-arachne-surface shrink-0">
      <span className="font-mono text-[10px] text-arachne-muted uppercase tracking-widest">
        Showing {startIndex} - {endIndex} of {filteredJobsCount} results
      </span>
      <div className="flex items-center gap-4">
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(prev => prev - 1)}
          className="text-arachne-muted hover:text-primary disabled:opacity-30 transition-colors font-mono text-[11px] uppercase"
        >
          &lt; Prev
        </button>
        <span className="font-mono text-[11px] text-arachne-text">{currentPage} / {totalPages || 1}</span>
        <button
          disabled={currentPage === totalPages || totalPages === 0}
          onClick={() => setCurrentPage(prev => prev + 1)}
          className="text-arachne-muted hover:text-primary disabled:opacity-30 transition-colors font-mono text-[11px] uppercase"
        >
          Next &gt;
        </button>
      </div>
    </div>
  );
};

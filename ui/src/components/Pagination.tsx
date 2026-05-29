import React from 'react';
import { LuChevronLeft, LuChevronRight } from "react-icons/lu";

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
    <div className="h-14 border-t border-arachne-border flex items-center justify-between px-6 md:px-8 bg-arachne-surface shrink-0">
      <div className="flex items-center gap-2 sm:gap-3">
        <div className="hidden xs:block h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
        <span className="font-mono text-[10px] sm:text-xs text-arachne-muted uppercase tracking-wider font-bold whitespace-nowrap">
          SHOWING <span className="text-arachne-text" style={{ fontVariantNumeric: 'tabular-nums' }}>{startIndex}-{endIndex}</span> OF <span className="text-primary">{filteredJobsCount}</span> RESULTS
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(prev => prev - 1)}
          className="h-8 w-8 flex items-center justify-center border border-arachne-border rounded-lg bg-arachne-surface-alt/50 text-arachne-muted hover:text-primary hover:border-primary/40 disabled:opacity-20 disabled:hover:border-arachne-border disabled:hover:text-arachne-muted transition-all"
          aria-label="Previous page"
        >
          <LuChevronLeft className="text-lg" />
        </button>
        
        <div className="px-3 h-8 flex items-center bg-arachne-surface-alt/30 border border-arachne-border rounded-lg font-mono text-xs font-bold text-arachne-text shadow-inner">
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{currentPage}</span>
          <span className="mx-2 text-arachne-muted/40">/</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{totalPages || 1}</span>
        </div>

        <button
          disabled={currentPage === totalPages || totalPages === 0}
          onClick={() => setCurrentPage(prev => prev + 1)}
          className="h-8 w-8 flex items-center justify-center border border-arachne-border rounded-lg bg-arachne-surface-alt/50 text-arachne-muted hover:text-primary hover:border-primary/40 disabled:opacity-20 disabled:hover:border-arachne-border disabled:hover:text-arachne-muted transition-all"
          aria-label="Next page"
        >
          <LuChevronRight className="text-lg" />
        </button>
      </div>
    </div>
  );
};

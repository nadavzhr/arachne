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
    <div className="min-h-[64px] py-2 border-t border-arachne-border flex flex-col sm:flex-row items-center justify-between px-4 md:px-8 bg-arachne-surface shrink-0 gap-3">
      <div className="flex items-center gap-2">
        <div className="hidden xs:block h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
        <span className="font-mono text-[10px] sm:text-xs text-arachne-muted uppercase tracking-wider font-bold">
          <span className="hidden sm:inline">SHOWING</span> <span className="text-arachne-text" style={{ fontVariantNumeric: 'tabular-nums' }}>{startIndex}-{endIndex}</span> <span className="text-arachne-muted/60">/</span> <span className="text-primary">{filteredJobsCount}</span> <span className="hidden sm:inline">RESULTS</span>
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(prev => prev - 1)}
          className="h-11 w-11 flex items-center justify-center border border-arachne-border rounded-xl bg-arachne-surface-alt/50 text-arachne-muted active:text-primary active:border-primary disabled:opacity-20 transition-all"
          aria-label="Previous page"
        >
          <LuChevronLeft className="text-xl" />
        </button>
        
        <div className="px-4 h-11 flex items-center bg-arachne-bg border border-arachne-border rounded-xl font-mono text-xs font-bold text-arachne-text shadow-inner">
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{currentPage}</span>
          <span className="mx-2 text-arachne-muted/40">/</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>{totalPages || 1}</span>
        </div>

        <button
          disabled={currentPage === totalPages || totalPages === 0}
          onClick={() => setCurrentPage(prev => prev + 1)}
          className="h-11 w-11 flex items-center justify-center border border-arachne-border rounded-xl bg-arachne-surface-alt/50 text-arachne-muted active:text-primary active:border-primary disabled:opacity-20 transition-all"
          aria-label="Next page"
        >
          <LuChevronRight className="text-xl" />
        </button>
      </div>
    </div>
  );
};

import { motion, type Variants } from 'framer-motion';
import { LuSearch, LuX, LuExternalLink, LuFilter } from 'react-icons/lu';
import type { JobPosting } from '../types/job';
import { CompanyLogo } from './CompanyLogo';

interface JobsTableProps {
  isLoading: boolean;
  error: Error | null;
  paginatedJobs: JobPosting[];
  selectedJob: JobPosting | null;
  setSelectedJob: (job: JobPosting | null) => void;
  // Filter props
  companyFilter: string;
  setCompanyFilter: (c: string) => void;
  uniqueCompanies: string[];
  locationFilter: string;
  setLocationFilter: (l: string) => void;
  uniqueLocations: string[];
  searchRole: string;
  setSearchRole: (role: string) => void;
}

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.03
    }
  }
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 4 },
  visible: { opacity: 1, y: 0 }
};

export const JobsTable = ({
  isLoading,
  error,
  paginatedJobs,
  selectedJob,
  setSelectedJob,
  companyFilter,
  setCompanyFilter,
  uniqueCompanies,
  locationFilter,
  setLocationFilter,
  uniqueLocations,
  searchRole,
  setSearchRole,
}: JobsTableProps) => {
  return (
    <div className="flex-1 flex flex-col min-h-0 bg-arachne-surface rounded-xl border border-arachne-border overflow-hidden m-2 md:m-8 shadow-sm">
      {/* Filter Bar */}
      <div className="shrink-0 px-4 py-3 border-b border-arachne-border bg-arachne-surface-alt/20 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-primary font-mono text-[10px] uppercase tracking-[0.2em] font-bold">
          <LuFilter className="text-xs" />
          <span className="hidden sm:inline">[ FILTERS ]</span>
        </div>
        
        {/* Search Input */}
        <div className="relative flex-1 min-w-[140px] max-w-md">
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            <LuSearch className="text-arachne-muted text-sm" />
          </div>
          <input
            className="w-full bg-arachne-surface border border-arachne-border rounded-lg pl-9 pr-9 py-2.5 text-xs font-mono uppercase tracking-tight focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-arachne-muted/40 h-[44px]"
            placeholder="Search roles..."
            type="text"
            value={searchRole}
            onChange={e => setSearchRole(e.target.value)}
          />
          {searchRole && (
            <button
              onClick={() => setSearchRole('')}
              className="absolute inset-y-0 right-3 flex items-center text-arachne-muted hover:text-primary transition-colors"
              aria-label="Clear search"
            >
              <LuX className="text-sm" />
            </button>
          )}
        </div>

        {/* Filters Group - Wrapped for Mobile */}
        <div className="flex items-center gap-3 w-full lg:w-auto">
          {/* Company Select */}
          <div className="relative flex-1 lg:min-w-[160px]">
            <select
              value={companyFilter}
              onChange={e => setCompanyFilter(e.target.value)}
              className="w-full bg-arachne-bg border border-arachne-border rounded-lg px-3 py-2 text-[10px] font-mono uppercase tracking-tighter focus:ring-1 focus:ring-primary focus:border-primary transition-all cursor-pointer appearance-none pr-8 text-arachne-text shadow-inner h-[44px]"
            >
              <option value="All">All Companies</option>
              {uniqueCompanies.filter(c => c !== 'All').map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-arachne-muted/50">
              <LuFilter className="text-[10px]" />
            </div>
          </div>

          {/* Location Select */}
          <div className="relative flex-1 lg:min-w-[160px]">
            <select
              value={locationFilter}
              onChange={e => setLocationFilter(e.target.value)}
              className="w-full bg-arachne-bg border border-arachne-border rounded-lg px-3 py-2 text-[10px] font-mono uppercase tracking-tighter focus:ring-1 focus:ring-primary focus:border-primary transition-all cursor-pointer appearance-none pr-8 text-arachne-text shadow-inner h-[44px]"
            >
              <option value="All">All Locations</option>
              {uniqueLocations.filter(l => l !== 'All').map(l => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-arachne-muted/50">
              <LuFilter className="text-[10px]" />
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto custom-scrollbar">
        {/* Desktop Table View */}
        <table className="hidden md:table w-full text-left border-collapse table-fixed">
          <thead className="sticky top-0 bg-arachne-surface z-10 border-b border-arachne-border shadow-sm">
            <tr>
              <th className="w-[220px] py-4 px-8 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em]">
                Company
              </th>
              <th className="py-4 px-6 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em]">
                Role / Title
              </th>
              <th className="w-[180px] py-4 px-6 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em]">
                Location
              </th>
              <th className="w-[120px] py-4 px-8 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em] text-right">
                Posted
              </th>
              <th className="w-[80px] py-4 px-8 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em] text-right">
                Link
              </th>
            </tr>
          </thead>
          <motion.tbody 
            className="divide-y divide-arachne-border"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {isLoading ? (
              <>
                {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                  <tr key={i} className="h-14 animate-pulse">
                    <td className="px-8"><div className="h-4 w-32 bg-arachne-surface-alt rounded" /></td>
                    <td className="px-6"><div className="h-4 w-64 bg-arachne-surface-alt rounded" /></td>
                    <td className="px-6"><div className="h-4 w-24 bg-arachne-surface-alt rounded" /></td>
                    <td className="px-8"><div className="h-4 w-16 bg-arachne-surface-alt rounded ml-auto" /></td>
                    <td className="px-8"><div className="h-4 w-8 bg-arachne-surface-alt rounded ml-auto" /></td>
                  </tr>
                ))}
              </>
            ) : error ? (
              <tr>
                <td colSpan={5} className="p-24 text-center text-primary font-mono text-xs tracking-[0.3em]">
                  [ CRITICAL_SYSTEM_FAILURE: SOURCE_OFFLINE ]
                </td>
              </tr>
            ) : paginatedJobs.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-24 text-center text-arachne-muted font-mono text-xs tracking-[0.3em]">
                  [ ZERO_NODES_DETECTED_IN_SECTOR ]
                </td>
              </tr>
            ) : (
              paginatedJobs.map(job => (
                <motion.tr
                  key={job.spider + job.external_id}
                  variants={itemVariants}
                  className={`
                    group hover:bg-arachne-surface-alt/40 cursor-pointer transition-all duration-200 h-14 relative
                    ${selectedJob === job ? 'bg-primary/5' : ''}
                  `}
                  onClick={() => setSelectedJob(job)}
                >
                  <td className="py-3 px-8 overflow-hidden relative">
                    <div className="flex items-center gap-3">
                      <CompanyLogo company={job.company} />
                      <span className="font-display font-bold text-sm tracking-tight truncate group-hover:text-primary transition-colors" title={job.company || 'Unknown'}>
                        {job.company || 'Unknown'}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-6 overflow-hidden">
                    <span className="font-body text-sm font-medium text-arachne-text truncate block w-full" title={job.title}>
                      {job.title}
                    </span>
                  </td>
                  <td className="py-3 px-6 overflow-hidden">
                    <span className="font-mono text-xs text-arachne-muted truncate block uppercase tracking-tighter" title={job.location || 'GLOBAL'}>
                      {job.location || 'GLOBAL'}
                    </span>
                  </td>
                  <td className="py-3 px-8 font-mono text-xs text-arachne-muted text-right whitespace-nowrap">
                    {job.posted_at ? new Date(job.posted_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '--/--'}
                  </td>
                  <td className="py-3 px-8 text-right">
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={event => event.stopPropagation()}
                      className="inline-flex items-center justify-center text-arachne-muted hover:text-primary transition-all p-2 hover:scale-110"
                      title="View Source"
                    >
                      <LuExternalLink className="text-lg" />
                    </a>
                  </td>
                </motion.tr>
              ))
            )}
          </motion.tbody>
        </table>

        {/* Mobile Card View */}
        <div className="md:hidden flex flex-col divide-y divide-arachne-border">
          {isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="p-4 space-y-3 animate-pulse">
                <div className="flex justify-between items-center">
                  <div className="h-4 w-24 bg-arachne-surface-alt rounded" />
                  <div className="h-4 w-12 bg-arachne-surface-alt rounded" />
                </div>
                <div className="h-5 w-full bg-arachne-surface-alt rounded" />
                <div className="h-4 w-32 bg-arachne-surface-alt rounded" />
              </div>
            ))
          ) : error ? (
            <div className="p-12 text-center text-primary font-mono text-[10px] uppercase tracking-widest">
              [ SYSTEM_FAILURE ]
            </div>
          ) : paginatedJobs.length === 0 ? (
            <div className="p-12 text-center text-arachne-muted font-mono text-[10px] uppercase tracking-widest">
              [ NO_RESULTS_FOUND ]
            </div>
          ) : (
            paginatedJobs.map(job => (
              <div
                key={job.spider + job.external_id}
                onClick={() => setSelectedJob(job)}
                className={`p-4 space-y-3 active:bg-primary/10 transition-colors ${selectedJob === job ? 'bg-primary/5' : ''}`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <CompanyLogo company={job.company} size="sm" />
                    <span className="font-display font-bold text-xs uppercase tracking-tight text-primary">
                      {job.company || 'Unknown'}
                    </span>
                  </div>
                  <span className="font-mono text-[10px] text-arachne-muted">
                    {job.posted_at ? new Date(job.posted_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '--/--'}
                  </span>
                </div>
                <h3 className="font-body text-sm font-bold text-arachne-text leading-snug">
                  {job.title}
                </h3>
                <div className="flex justify-between items-center">
                  <span className="font-mono text-[10px] text-arachne-muted uppercase tracking-tighter">
                    {job.location || 'GLOBAL'}
                  </span>
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={e => e.stopPropagation()}
                    className="h-9 w-9 flex items-center justify-center bg-arachne-surface-alt border border-arachne-border rounded-lg text-arachne-muted active:text-primary active:border-primary transition-colors"
                  >
                    <LuExternalLink className="text-lg" />
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

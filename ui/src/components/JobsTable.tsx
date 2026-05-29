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
    <div className="flex-1 flex flex-col min-h-0 bg-arachne-surface rounded-2xl border border-arachne-border overflow-hidden m-4 md:m-8 shadow-sm">
      {/* Filter Bar */}
      <div className="shrink-0 px-6 py-4 border-b border-arachne-border bg-arachne-surface-alt/20 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2 text-primary font-mono text-[10px] uppercase tracking-[0.2em] font-bold">
          <LuFilter className="text-xs" />
          [ FILTERS ]
        </div>
        
        {/* Search Input */}
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            <LuSearch className="text-arachne-muted text-sm" />
          </div>
          <input
            className="w-full bg-arachne-surface border border-arachne-border rounded-xl pl-9 pr-9 py-2 text-xs font-mono uppercase tracking-tight focus:ring-1 focus:ring-primary focus:border-primary transition-all placeholder:text-arachne-muted/40"
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

        {/* Company Select */}
        <div className="relative min-w-[160px]">
          <select
            value={companyFilter}
            onChange={e => setCompanyFilter(e.target.value)}
            className="w-full bg-arachne-bg border border-arachne-border rounded-xl px-3 py-2 text-[10px] font-mono uppercase tracking-tighter focus:ring-1 focus:ring-primary focus:border-primary transition-all cursor-pointer appearance-none pr-8 text-arachne-text shadow-inner"
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
        <div className="relative min-w-[160px]">
          <select
            value={locationFilter}
            onChange={e => setLocationFilter(e.target.value)}
            className="w-full bg-arachne-bg border border-arachne-border rounded-xl px-3 py-2 text-[10px] font-mono uppercase tracking-tighter focus:ring-1 focus:ring-primary focus:border-primary transition-all cursor-pointer appearance-none pr-8 text-arachne-text shadow-inner"
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

      {/* Table Area */}
      <div className="flex-1 overflow-auto custom-scrollbar">
        <table className="jobs-table w-full text-left border-collapse table-fixed min-w-[900px]">
          <thead className="sticky top-0 bg-arachne-surface z-10 border-b border-arachne-border shadow-sm">
            <tr>
              <th className="w-[220px] py-4 px-6 md:px-8 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em]">
                Company
              </th>
              <th className="py-4 px-6 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em]">
                Role / Title
              </th>
              <th className="w-[180px] py-4 px-6 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em]">
                Location
              </th>
              <th className="w-[120px] py-4 px-6 md:px-8 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em] text-right">
                Posted
              </th>
              <th className="w-[80px] py-4 px-6 md:px-8 font-mono text-[10px] uppercase text-arachne-muted font-bold tracking-[0.2em] text-right">
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
                    <td className="px-6 md:px-8"><div className="h-4 w-32 bg-arachne-surface-alt rounded" /></td>
                    <td className="px-6"><div className="h-4 w-64 bg-arachne-surface-alt rounded" /></td>
                    <td className="px-6"><div className="h-4 w-24 bg-arachne-surface-alt rounded" /></td>
                    <td className="px-6 md:px-8"><div className="h-4 w-16 bg-arachne-surface-alt rounded ml-auto" /></td>
                    <td className="px-6 md:px-8"><div className="h-4 w-8 bg-arachne-surface-alt rounded ml-auto" /></td>
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
                    ${selectedJob === job ? 'bg-arachne-surface-alt/80' : ''}
                  `}
                  onClick={() => setSelectedJob(job)}
                >
                  <td className="py-3 px-6 md:px-8 overflow-hidden relative">
                    {/* Active Accent */}
                    <div className={`
                      absolute left-0 top-0 bottom-0 w-[2.5px] bg-primary transition-all duration-300 origin-left
                      ${selectedJob === job ? 'scale-x-100 shadow-[0_0_12px_rgba(219,44,31,0.6)]' : 'scale-x-0 group-hover:scale-x-100 group-hover:shadow-[0_0_8px_rgba(219,44,31,0.4)]'}
                    `} />
                    
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
                  <td className="py-3 px-6 md:px-8 font-mono text-xs text-arachne-muted text-right whitespace-nowrap">
                    {job.posted_at ? new Date(job.posted_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '--/--'}
                  </td>
                  <td className="py-3 px-6 md:px-8 text-right">
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      onClick={event => event.stopPropagation()}
                      className="inline-flex items-center justify-center text-arachne-muted hover:text-primary transition-all p-1 hover:scale-110"
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
      </div>
    </div>
  );
};

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
    <div className="flex-1 overflow-auto">
      <table className="jobs-table w-full text-left border-collapse relative min-w-full sm:min-w-[780px]">
        <thead className="sticky top-0 bg-arachne-surface z-10 border-b border-arachne-border">
          <tr>
            <th className="col-company py-4 px-4 md:px-8 font-mono text-[11px] uppercase text-arachne-muted font-normal tracking-wider">
              <div className="flex items-center gap-2">
                <span className="shrink-0">Company:</span>
                <select
                  value={companyFilter}
                  onChange={e => setCompanyFilter(e.target.value)}
                  className="bg-transparent border-none text-[10px] font-mono focus:ring-0 p-0 pr-6 cursor-pointer text-arachne-text uppercase flex-1 min-w-0 filter-select"
                >
                  {uniqueCompanies.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </th>
            <th className="col-role py-4 px-4 font-mono text-[11px] uppercase text-arachne-muted font-normal tracking-wider">
              <div className="flex items-center gap-2">
                <span className="shrink-0">Role:</span>
                <input
                  className="font-mono text-[10px] bg-transparent border-0 focus:ring-0 flex-1 min-w-0 placeholder:text-arachne-muted text-arachne-text p-0 focus:outline-none uppercase"
                  placeholder="[ SEARCH... ]"
                  type="text"
                  value={searchRole}
                  onChange={e => setSearchRole(e.target.value)}
                />
              </div>
            </th>
            <th className="col-apply-mobile py-4 px-4 font-mono text-[11px] uppercase text-arachne-muted font-normal tracking-wider text-right align-top"></th>
            <th className="col-location py-4 px-4 font-mono text-[11px] uppercase text-arachne-muted font-normal tracking-wider">
              <div className="flex items-center gap-2">
                <span className="shrink-0">Location:</span>
                <select
                  value={locationFilter}
                  onChange={e => setLocationFilter(e.target.value)}
                  className="bg-transparent border-none text-[10px] font-mono focus:ring-0 p-0 pr-6 cursor-pointer text-arachne-text uppercase flex-1 min-w-0 filter-select"
                >
                  {uniqueLocations.map(l => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </div>
            </th>
            <th className="col-date py-4 px-4 md:px-8 font-mono text-[11px] uppercase text-arachne-muted font-normal tracking-wider text-right align-top">Date</th>
            <th className="col-apply py-4 px-4 md:px-8 font-mono text-[11px] uppercase text-arachne-muted font-normal tracking-wider text-right w-24 align-top">Apply</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-arachne-border">
          {isLoading ? (
            <tr>
              <td colSpan={6} className="p-20 text-center text-arachne-muted animate-pulse font-mono">
                SCANNING ACTIVE THREADS...
              </td>
            </tr>
          ) : error ? (
            <tr>
              <td colSpan={6} className="p-20 text-center text-arachne-muted font-mono">
                FAILED TO LOAD JOBS.JSON
              </td>
            </tr>
          ) : paginatedJobs.length === 0 ? (
            <tr>
              <td colSpan={6} className="p-20 text-center text-arachne-muted font-mono">
                NO JOBS FOUND. RUN ARACHNE EXPORT TO REFRESH.
              </td>
            </tr>
          ) : (
            paginatedJobs.map(job => (
              <tr
                key={job.spider + job.external_id}
                className={`group hover:bg-arachne-surface-alt cursor-pointer transition-colors h-16 ${selectedJob === job ? 'bg-arachne-surface-alt' : ''}`}
                onClick={() => setSelectedJob(job)}
              >
                <td className="col-company py-3 px-4 md:px-8 whitespace-nowrap">
                  <div className="flex items-center gap-4">
                    <CompanyLogo company={job.company} />
                    <span className="font-display font-bold text-sm tracking-tight">{job.company || 'Unknown'}</span>
                  </div>
                </td>
                <td className="col-role py-3 px-4">
                  <div className="flex items-center gap-2">
                    <span className="font-body text-sm font-medium text-arachne-text line-clamp-1">{job.title}</span>
                  </div>
                </td>
                <td className="col-apply-mobile py-3 px-4 whitespace-nowrap text-right">
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={event => event.stopPropagation()}
                    className="inline-flex items-center justify-center border border-arachne-border bg-arachne-surface-alt text-arachne-text hover:text-primary hover:border-primary transition-colors h-7 w-7"
                    aria-label="Open application"
                  >
                    <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                  </a>
                </td>
                <td className="col-location py-3 px-4 whitespace-nowrap font-mono text-[11px] text-arachne-muted truncate">{job.location || 'GLOBAL'}</td>
                <td className="col-date py-3 px-4 md:px-8 whitespace-nowrap font-mono text-[11px] text-arachne-muted text-right">
                  {job.posted_at ? new Date(job.posted_at).toLocaleDateString() : '-- -- --'}
                </td>
                <td className="col-apply py-3 px-4 md:px-8 whitespace-nowrap text-right">
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={event => event.stopPropagation()}
                    className="inline-flex items-center justify-center border border-arachne-border bg-arachne-bg text-[10px] font-mono uppercase tracking-widest px-3 py-1.5 text-arachne-text hover:text-primary hover:border-primary hover:bg-arachne-surface-alt transition-colors"
                  >
                    Apply
                  </a>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

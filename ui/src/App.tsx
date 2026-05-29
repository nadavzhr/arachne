import { useEffect, useMemo, useState } from 'react';
import { useJobs } from './hooks/useJobs';
import type { JobPosting } from './types/job';
import {
  Header,
  JobsTable,
  Pagination,
  PayloadDrawer,
  Sidebar,
  AnalyticsView,
  SystemView,
  ExportDialog,
} from './components';
import type { ViewType } from './components/Sidebar';

export default function App() {
  const { data: jobs = [], isLoading, error } = useJobs();
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
  const [activeView, setActiveView] = useState<ViewType>('jobs');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window === 'undefined') {
      return 'light';
    }
    const stored = window.localStorage.getItem('arachne-theme');
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });
  
  // Filters
  const [searchRole, setSearchRole] = useState('');
  const [companyFilter, setCompanyFilter] = useState('All');
  const [locationFilter, setLocationFilter] = useState('All');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 11;

  const uniqueCompanies = useMemo(() => ['All', ...new Set(jobs.map(j => j.company || 'Unknown').filter(Boolean))], [jobs]);
  const uniqueLocations = useMemo(() => {
    const locations = jobs.map(j => {
      if (!j.location) return 'N/A';
      return j.location.split(',')[0].trim(); // Get city/top level
    });
    return ['All', ...new Set(locations)];
  }, [jobs]);

  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      const matchesRole = job.title.toLowerCase().includes(searchRole.toLowerCase());
      const matchesCompany = companyFilter === 'All' || job.company === companyFilter;
      const matchesLocation = locationFilter === 'All' || (job.location?.includes(locationFilter));
      return matchesRole && matchesCompany && matchesLocation;
    });
  }, [jobs, searchRole, companyFilter, locationFilter]);

  const totalPages = Math.ceil(filteredJobs.length / itemsPerPage);
  const paginatedJobs = filteredJobs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleExport = (format: 'json' | 'csv') => {
    let content: string;
    let mimeType: string;
    let fileName: string;

    if (format === 'json') {
      content = JSON.stringify(filteredJobs, null, 2);
      mimeType = 'application/json';
      fileName = 'arachne_jobs.json';
    } else {
      // CSV generation
      const headers = ['spider', 'company', 'title', 'location', 'posted_at', 'url'];
      const rows = filteredJobs.map(job => [
        job.spider,
        job.company || '',
        `"${(job.title || '').replace(/"/g, '""')}"`,
        `"${(job.location || '').replace(/"/g, '""')}"`,
        job.posted_at || '',
        job.url
      ]);
      content = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      mimeType = 'text/csv';
      fileName = 'arachne_jobs.csv';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-light', 'theme-dark');
    root.classList.add(`theme-${theme}`);
    window.localStorage.setItem('arachne-theme', theme);
  }, [theme]);

  return (
    <div className="bg-arachne-bg text-arachne-text min-h-screen w-full flex flex-col overflow-hidden bg-grid font-body">
      <Header 
        theme={theme} 
        setTheme={setTheme} 
        exportToJson={() => setIsExportDialogOpen(true)}
        toggleSidebar={() => setIsSidebarOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar 
          activeView={activeView} 
          setActiveView={setActiveView} 
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main className="flex-1 overflow-hidden relative z-0 flex flex-col w-full">
          {activeView === 'jobs' ? (
            <div className="flex-1 bg-arachne-surface flex flex-col h-full overflow-hidden">
              <JobsTable 
                isLoading={isLoading}
                error={error}
                paginatedJobs={paginatedJobs}
                selectedJob={selectedJob}
                setSelectedJob={setSelectedJob}
                companyFilter={companyFilter}
                setCompanyFilter={setCompanyFilter}
                uniqueCompanies={uniqueCompanies}
                locationFilter={locationFilter}
                setLocationFilter={setLocationFilter}
                uniqueLocations={uniqueLocations}
                searchRole={searchRole}
                setSearchRole={setSearchRole}
              />

              <Pagination 
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
                totalPages={totalPages}
                itemsPerPage={itemsPerPage}
                filteredJobsCount={filteredJobs.length}
              />
            </div>
          ) : activeView === 'analytics' ? (
            <AnalyticsView />
          ) : (
            <SystemView />
          )}
        </main>
      </div>

      <PayloadDrawer 
        selectedJob={selectedJob}
        setSelectedJob={setSelectedJob}
      />

      <ExportDialog 
        isOpen={isExportDialogOpen}
        onClose={() => setIsExportDialogOpen(false)}
        onExport={handleExport}
      />
    </div>
  );
}

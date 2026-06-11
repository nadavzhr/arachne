import { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  const itemsPerPage = 12; // Increased slightly for better fit

  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchRole, companyFilter, locationFilter]);

  const uniqueCompanies = useMemo(() => ['All', ...new Set(jobs.map(j => j.company || 'Unknown').filter(Boolean))], [jobs]);
  const uniqueLocations = useMemo(() => {
    const locations = jobs.map(j => {
      if (!j.location) return 'N/A';
      return j.location.split(',')[0].trim();
    });
    return ['All', ...new Set(locations)];
  }, [jobs]);

  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      const matchesRole = job.title.toLowerCase().includes(searchRole.toLowerCase());
      const matchesCompany = companyFilter === 'All' || job.company === companyFilter;
      
      const jobLocation = job.location ? job.location.split(',')[0].trim() : 'N/A';
      const matchesLocation = locationFilter === 'All' || jobLocation === locationFilter;
      
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
    <div className="bg-arachne-bg text-arachne-text h-dvh w-full flex flex-col overflow-hidden bg-grid font-body selection:bg-primary/10">
      <Header 
        theme={theme} 
        setTheme={setTheme} 
        exportToJson={() => setIsExportDialogOpen(true)}
        toggleSidebar={() => setIsSidebarOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar 
          activeView={activeView} 
          setActiveView={setActiveView} 
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        <main className="flex-1 min-h-0 overflow-hidden relative z-0 flex flex-col w-full bg-arachne-surface pb-[env(safe-area-inset-bottom)]">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeView}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="flex-1 flex flex-col min-h-0 h-full overflow-hidden"
            >
              {activeView === 'jobs' ? (
                <>
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
                </>
              ) : activeView === 'analytics' ? (
                <AnalyticsView />
              ) : (
                <SystemView />
              )}
            </motion.div>
          </AnimatePresence>
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

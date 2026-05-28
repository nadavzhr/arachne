import { useEffect, useMemo, useState } from 'react';
import { useJobs } from './hooks/useJobs';
import type { JobPosting } from './types/job';
import {
  Header,
  JobsTable,
  Pagination,
  PayloadDrawer,
} from './components';

export default function App() {
  const { data: jobs = [], isLoading, error } = useJobs();
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null);
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
  const [itemsPerPage, setItemsPerPage] = useState(10);

  useEffect(() => {
    const calculateItemsPerPage = () => {
      // Header (64) + Table Header (52) + Pagination (56) + Buffer/Padding (~20) = ~192px
      const fixedHeight = 192;
      const rowHeight = 64; // h-16 is 64px
      const availableHeight = window.innerHeight - fixedHeight;
      const calculatedCount = Math.max(5, Math.floor(availableHeight / rowHeight));
      setItemsPerPage(calculatedCount);
    };

    calculateItemsPerPage();
    window.addEventListener('resize', calculateItemsPerPage);
    return () => window.removeEventListener('resize', calculateItemsPerPage);
  }, []);

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

  const exportToJson = () => {
    if (!window.confirm("Are you sure you want to download the current filtered jobs to a JSON file?")) {
      return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredJobs, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", "arachne_jobs.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
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
        exportToJson={exportToJson} 
      />

      <main className="flex-1 overflow-hidden relative z-0 flex flex-col md:flex-row w-full">
        <div className="flex-1 bg-arachne-surface border-r border-arachne-border flex flex-col h-full overflow-hidden">
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
      </main>

      <PayloadDrawer 
        selectedJob={selectedJob}
        setSelectedJob={setSelectedJob}
      />
    </div>
  );
}

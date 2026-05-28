import type { JobPosting } from '../types/job';
import { CompanyLogo } from './CompanyLogo';

interface PayloadDrawerProps {
  selectedJob: JobPosting | null;
  setSelectedJob: (job: JobPosting | null) => void;
}

export const PayloadDrawer = ({ selectedJob, setSelectedJob }: PayloadDrawerProps) => {
  return (
    <>
      {/* Backdrop */}
      {selectedJob && (
        <div 
          className="fixed inset-0 bg-black/60 z-[100] transition-opacity duration-300"
          onClick={() => setSelectedJob(null)}
        />
      )}

      <aside
        className={`fixed inset-y-0 right-0 w-full md:w-[600px] bg-arachne-surface border-l border-arachne-border flex flex-col z-[110] transition-transform duration-300 shadow-2xl ${selectedJob ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {selectedJob && (
          <>
            <div className="h-16 border-b border-arachne-border flex items-center justify-between px-6 shrink-0 bg-arachne-surface sticky top-0 z-10">
              <h2 className="font-display font-bold text-lg">Raw Payload</h2>
              <button
                className="text-arachne-muted hover:text-primary transition-colors p-2 rounded-full border border-arachne-border bg-arachne-surface-alt"
                onClick={() => setSelectedJob(null)}
                aria-label="Close"
              >
                <span className="material-symbols-outlined text-2xl">close</span>
              </button>
            </div>

            <div className="p-8 border-b border-arachne-border bg-arachne-surface-alt">
              <div className="flex flex-col gap-6">
                <div className="flex items-center gap-4">
                  <CompanyLogo company={selectedJob.company} />
                  <div className="flex flex-col">
                    <h3 className="font-display font-bold text-xl leading-tight">{selectedJob.title}</h3>
                    <p className="text-sm text-arachne-muted">{selectedJob.company}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="flex flex-col">
                    <span className="text-[10px] font-mono text-arachne-muted uppercase mb-1">Status</span>
                    <span
                      className={`text-xs font-mono w-fit px-2 py-0.5 border ${selectedJob.remote ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-500' : 'border-arachne-border bg-arachne-bg text-arachne-muted'}`}
                    >
                      {selectedJob.remote ? 'REMOTE_OK' : 'ON_SITE'}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] font-mono text-arachne-muted uppercase mb-1">Source</span>
                    <span className="text-xs font-mono uppercase">{selectedJob.spider}</span>
                  </div>
                </div>
                <a
                  href={selectedJob.url}
                  target="_blank"
                  rel="noreferrer"
                  className="bg-primary text-white text-center py-3 font-display font-bold text-sm hover:brightness-110 transition-all"
                >
                  OPEN EXTERNAL APPLICATION
                </a>
              </div>
            </div>

            <div className="flex-1 overflow-auto bg-arachne-code-bg p-6">
              <pre className="font-mono text-[11px] leading-relaxed text-arachne-code-text whitespace-pre-wrap break-all">
                {JSON.stringify(selectedJob, null, 2)}
              </pre>
            </div>
          </>
        )}
      </aside>
    </>
  );
};

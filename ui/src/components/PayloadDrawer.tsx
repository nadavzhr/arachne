import { motion, AnimatePresence } from 'framer-motion';
import { LuX, LuExternalLink, LuZap, LuCode } from 'react-icons/lu';
import type { JobPosting } from '../types/job';
import { CompanyLogo } from './CompanyLogo';

interface PayloadDrawerProps {
  selectedJob: JobPosting | null;
  setSelectedJob: (job: JobPosting | null) => void;
}

export const PayloadDrawer = ({ selectedJob, setSelectedJob }: PayloadDrawerProps) => {
  return (
    <AnimatePresence>
      {selectedJob && (
        <>
          {/* Backdrop */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 z-[100] backdrop-blur-sm"
            onClick={() => setSelectedJob(null)}
          />

          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween', duration: 0.3, ease: [0.25, 1, 0.5, 1] }}
            className="fixed inset-y-0 right-0 w-full md:w-[600px] bg-arachne-surface border-l border-arachne-border flex flex-col z-[110] shadow-2xl pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]"
          >
            <div className="h-16 md:h-20 border-b border-arachne-border flex items-center justify-between px-6 md:px-8 shrink-0 bg-arachne-surface sticky top-0 z-10">
              <div className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                <h2 className="font-display font-bold text-[10px] md:text-sm uppercase tracking-[0.2em] text-arachne-muted">Job_Posting_Details</h2>
              </div>
              <button
                className="h-11 w-11 flex items-center justify-center text-arachne-muted active:text-primary transition-all rounded-xl border border-arachne-border bg-arachne-surface-alt/50 active:border-primary/30"
                onClick={() => setSelectedJob(null)}
                aria-label="Close"
              >
                <LuX className="text-2xl" />
              </button>
            </div>

            <div className="flex flex-col flex-1 min-h-0">
              <div className="p-6 md:p-10 border-b border-arachne-border bg-arachne-surface-alt/30">
                <div className="flex flex-col gap-6 md:gap-8">
                  <div className="flex items-center gap-4 md:gap-6">
                    <div className="shrink-0 scale-90 md:scale-100">
                      <CompanyLogo company={selectedJob.company} />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <h3 className="font-display font-bold text-xl md:text-2xl leading-tight text-arachne-text break-words">{selectedJob.title}</h3>
                      <p className="text-sm font-mono text-primary font-bold uppercase tracking-widest truncate">{selectedJob.company}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 md:gap-8">
                    <div className="flex flex-col gap-2">
                      <span className="text-[10px] font-mono text-arachne-muted uppercase tracking-widest font-bold flex items-center gap-2">
                        <LuZap className="text-xs text-primary" /> Work_Model
                      </span>
                      <span
                        className={`text-xs font-mono w-fit px-3 py-1 rounded-lg border font-bold ${selectedJob.remote ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-500' : 'border-arachne-border bg-arachne-bg text-arachne-muted'}`}
                      >
                        {selectedJob.remote ? 'REMOTE' : 'OFFICE'}
                      </span>
                    </div>
                    <div className="flex flex-col gap-2">
                      <span className="text-[10px] font-mono text-arachne-muted uppercase tracking-widest font-bold flex items-center gap-2">
                        <LuCode className="text-xs text-primary" /> Data_Source
                      </span>
                      <span className="text-xs font-mono uppercase font-bold text-arachne-text px-3 py-1 bg-arachne-bg border border-arachne-border rounded-lg w-fit">
                        {selectedJob.spider}
                      </span>
                    </div>
                  </div>

                  <a
                    href={selectedJob.url}
                    target="_blank"
                    rel="noreferrer"
                    className="bg-primary text-white text-center py-4 rounded-xl font-display font-bold text-sm active:brightness-110 transition-all shadow-[0_0_20px_oklch(var(--arachne-primary)/0.2)] flex items-center justify-center gap-3 group uppercase tracking-widest min-h-[56px]"
                  >
                    Apply Now
                    <LuExternalLink className="text-lg group-active:translate-x-1 group-active:-translate-y-1 transition-transform" />
                  </a>
                </div>
              </div>

              <div className="flex-1 overflow-auto bg-arachne-code-bg p-6 md:p-8 custom-scrollbar">
                <div className="flex items-center gap-3 mb-6 opacity-40">
                  <LuCode className="text-primary text-sm" />
                  <span className="text-[10px] font-mono text-arachne-code-text uppercase tracking-[0.3em] font-bold">Raw_Payload</span>
                </div>
                <pre className="font-mono text-[11px] leading-relaxed text-arachne-code-text whitespace-pre-wrap break-all border-l border-primary/20 pl-4 md:pl-6">
                  {JSON.stringify(selectedJob, null, 2)}
                </pre>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
};

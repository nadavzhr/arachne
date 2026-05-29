import { motion, type Variants } from 'framer-motion';
import { useSystemConfig } from '../hooks/useSystemConfig';
import { LuCpu, LuShieldCheck, LuBoxes, LuZap, LuDatabase, LuTerminal, LuCode, LuSearch, LuClock } from "react-icons/lu";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const sectionVariants: Variants = {
  hidden: { opacity: 0, x: -10 },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: { duration: 0.4, ease: "easeOut" }
  }
};

export const SystemView = () => {
  const { data, isLoading, error } = useSystemConfig();

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col min-h-0 overflow-y-auto bg-grid p-4 md:p-8 h-full">
        <div className="max-w-4xl mx-auto space-y-12 pb-12 w-full animate-pulse">
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-arachne-surface-alt" />
              <div className="space-y-2">
                <div className="h-6 w-48 bg-arachne-surface-alt rounded-md" />
                <div className="h-3 w-32 bg-arachne-surface-alt rounded-md" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="h-64 bg-arachne-surface-alt/50 border border-arachne-border rounded-2xl" />
              <div className="h-64 bg-arachne-surface-alt/50 border border-arachne-border rounded-2xl" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-primary uppercase tracking-widest text-xs">
        [ SYSTEM_ERROR ] SYSTEM_BLUEPRINT_COMPROMISED
      </div>
    );
  }

  const { engine, profile } = data;

  return (
    <motion.div 
      className="flex-1 flex flex-col min-h-0 overflow-y-auto bg-grid p-4 md:p-8 custom-scrollbar h-full"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="max-w-4xl mx-auto space-y-12 pb-12 w-full">
        
        {/* Profile Section */}
        <motion.section variants={sectionVariants} className="space-y-6">
          <div className="flex items-center gap-4 mb-8">
            <div className="h-12 w-12 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-center text-primary shadow-[0_0_15px_rgba(219,44,31,0.1)]">
              <LuShieldCheck className="text-2xl" />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold uppercase tracking-tight">Active Profile</h1>
              <p className="text-[10px] font-mono text-arachne-muted uppercase tracking-[0.2em]">Protocol_ID: <span className="text-arachne-text font-bold">{profile?.name}</span></p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-arachne-surface border border-arachne-border rounded-2xl p-8 space-y-6 shadow-sm group hover:border-primary/20 transition-colors">
              <div className="flex items-center gap-2 text-primary font-mono text-[10px] uppercase tracking-[0.2em] font-bold border-b border-arachne-border/50 pb-3">
                <LuSearch className="text-sm" /> [ SEARCH_CRITERIA ]
              </div>
              <div className="space-y-5">
                <div>
                  <div className="text-[9px] font-mono text-arachne-muted uppercase mb-2 tracking-widest">Target Title</div>
                  <div className="text-xl font-display font-bold text-arachne-text uppercase tracking-tight italic underline decoration-primary/40 decoration-2 underline-offset-4">
                    {profile?.search?.title}
                  </div>
                </div>
                <div>
                  <div className="text-[9px] font-mono text-arachne-muted uppercase mb-3 tracking-widest">Deployment Zones</div>
                  <div className="flex flex-wrap gap-2">
                    {profile?.search?.locations?.map((loc: string) => (
                      <span key={loc} className="px-3 py-1 bg-arachne-surface-alt/50 border border-arachne-border text-[10px] font-mono rounded-lg uppercase tracking-tight text-arachne-muted hover:text-primary hover:border-primary/30 transition-colors">
                        {loc}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-arachne-surface border border-arachne-border rounded-2xl p-8 shadow-sm group hover:border-primary/20 transition-colors">
              <div className="flex items-center gap-2 text-primary font-mono text-[10px] uppercase tracking-[0.2em] font-bold border-b border-arachne-border/50 pb-3 mb-6">
                <LuCode className="text-sm" /> [ FILTERING_LOGIC ]
              </div>
              <div className="space-y-6">
                {['title', 'location', 'company']?.map((field) => (
                  <div key={field} className="space-y-3">
                    <div className="text-[9px] font-mono text-arachne-muted uppercase tracking-widest flex items-center justify-between">
                      {field} Filters
                      <div className="h-px flex-1 bg-arachne-border/30 ml-4" />
                    </div>
                    <div className="space-y-2">
                      {profile?.filters?.[field]?.include_keywords?.length > 0 && (
                        <div className="flex items-start gap-3">
                          <span className="text-[9px] font-mono text-green-500 uppercase mt-1 font-bold shrink-0">MUST_INC:</span>
                          <div className="flex flex-wrap gap-1.5">
                            {profile?.filters?.[field]?.include_keywords?.map((kw: string) => (
                              <code key={kw} className="text-[10px] bg-green-500/5 text-green-600/90 px-2 py-0.5 rounded-md border border-green-500/10">"{kw}"</code>
                            ))}
                          </div>
                        </div>
                      )}
                      {profile?.filters?.[field]?.exclude_keywords?.length > 0 && (
                        <div className="flex items-start gap-3">
                          <span className="text-[9px] font-mono text-red-500 uppercase mt-1 font-bold shrink-0">MUST_EXC:</span>
                          <div className="flex flex-wrap gap-1.5">
                            {profile?.filters?.[field]?.exclude_keywords?.map((kw: string) => (
                              <code key={kw} className="text-[10px] bg-red-500/5 text-red-600/90 px-2 py-0.5 rounded-md border border-red-500/10">"{kw}"</code>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>

        {/* Engine Config */}
        <motion.section variants={sectionVariants} className="space-y-6">
          <div className="flex items-center gap-4 mb-8">
            <div className="h-12 w-12 rounded-xl bg-primary/5 border border-primary/20 flex items-center justify-center text-primary shadow-[0_0_15px_rgba(219,44,31,0.1)]">
              <LuCpu className="text-2xl" />
            </div>
            <div>
              <h2 className="text-xl font-display font-bold uppercase tracking-tight">Engine Core</h2>
              <p className="text-[10px] font-mono text-arachne-muted uppercase tracking-[0.2em]">Hardware_Configuration</p>
            </div>
          </div>

          <div className="bg-arachne-surface border border-arachne-border rounded-2xl overflow-hidden shadow-sm group hover:border-primary/20 transition-colors">
            <table className="w-full text-left font-mono text-xs">
              <tbody className="divide-y divide-arachne-border/50">
                {[
                  { label: 'Network Concurrency', value: engine?.concurrency, icon: LuBoxes },
                  { label: 'Request Staggering', value: engine?.request_concurrency, icon: LuZap },
                  { label: 'Sync Timeout', value: engine?.timeout_seconds ? `${engine.timeout_seconds}s` : 'N/A', icon: LuClock },
                  { label: 'System Agent', value: engine?.user_agent, icon: LuTerminal },
                  { label: 'Persistence Layer', value: 'SQLite_Datastore', icon: LuDatabase },
                ].map((row) => (
                  <tr key={row.label} className="hover:bg-arachne-surface-alt/50 transition-all group/row">
                    <td className="py-5 px-8 text-arachne-muted uppercase flex items-center gap-4 text-[10px] font-bold tracking-widest transition-colors group-hover/row:text-primary">
                      <row.icon className="text-primary/40 text-base group-hover/row:text-primary transition-colors" />
                      {row.label}
                    </td>
                    <td className="py-5 px-8 text-arachne-text font-bold truncate max-w-xs transition-colors group-hover/row:text-primary">
                      {row.value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.section>
      </div>
    </motion.div>
  );
};

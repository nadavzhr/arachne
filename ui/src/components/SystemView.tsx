import { useSystemConfig } from '../hooks/useSystemConfig';
import { LuCpu, LuShieldCheck, LuBoxes, LuZap, LuDatabase, LuTerminal, LuCode, LuSearch, LuClock } from "react-icons/lu";

export const SystemView = () => {
  const { data, isLoading, error } = useSystemConfig();

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-arachne-muted animate-pulse">
        DECRYPTING SYSTEM BLUEPRINT...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-red-500">
        ERROR: SYSTEM BLUEPRINT COMPROMISED
      </div>
    );
  }

  const { engine, profile } = data;

  return (
    <div className="flex-1 overflow-auto bg-grid p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Profile Section */}
        <section className="space-y-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <LuShieldCheck className="text-2xl" />
            </div>
            <div>
              <h1 className="text-2xl font-display font-bold uppercase tracking-tight">Active Profile</h1>
              <p className="text-xs font-mono text-arachne-muted uppercase tracking-widest">Protocol: {profile?.name}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-arachne-surface border border-arachne-border rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-primary font-mono text-xs uppercase tracking-wider mb-2">
                <LuSearch className="text-sm" /> Search Criteria
              </div>
              <div className="space-y-3">
                <div>
                  <div className="text-[10px] font-mono text-arachne-muted uppercase mb-1">Target Title</div>
                  <div className="text-lg font-display font-bold text-arachne-text uppercase tracking-tight italic underline decoration-primary/30 decoration-2 underline-offset-4">{profile?.search?.title}</div>
                </div>
                <div>
                  <div className="text-[10px] font-mono text-arachne-muted uppercase mb-1">Deployment Zones</div>
                  <div className="flex flex-wrap gap-2">
                    {profile?.search?.locations?.map((loc: string) => (
                      <span key={loc} className="px-2 py-0.5 bg-arachne-surface-alt border border-arachne-border text-[10px] font-mono rounded uppercase">{loc}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-arachne-surface border border-arachne-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-primary font-mono text-xs uppercase tracking-wider mb-4">
                <LuCode className="text-sm" /> Filtering Logic
              </div>
              <div className="space-y-4">
                {['title', 'location', 'company']?.map((field) => (
                  <div key={field} className="space-y-2">
                    <div className="text-[10px] font-mono text-arachne-muted uppercase border-b border-arachne-border/50 pb-1">{field} Filters</div>
                    <div className="space-y-1.5">
                      {profile?.filters?.[field]?.include_keywords?.length > 0 && (
                        <div className="flex items-start gap-2">
                          <span className="text-[9px] font-mono text-green-500 uppercase mt-0.5">MUST_INC:</span>
                          <div className="flex flex-wrap gap-1">
                            {profile?.filters?.[field]?.include_keywords?.map((kw: string) => (
                              <code key={kw} className="text-[10px] bg-green-500/5 text-green-400 px-1 rounded">"{kw}"</code>
                            ))}
                          </div>
                        </div>
                      )}
                      {profile?.filters?.[field]?.exclude_keywords?.length > 0 && (
                        <div className="flex items-start gap-2">
                          <span className="text-[9px] font-mono text-red-500 uppercase mt-0.5">MUST_EXC:</span>
                          <div className="flex flex-wrap gap-1">
                            {profile?.filters?.[field]?.exclude_keywords?.map((kw: string) => (
                              <code key={kw} className="text-[10px] bg-red-500/5 text-red-400 px-1 rounded">"{kw}"</code>
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
        </section>

        {/* Engine Config */}
        <section className="space-y-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <LuCpu className="text-2xl" />
            </div>
            <div>
              <h2 className="text-xl font-display font-bold uppercase tracking-tight">Engine Core</h2>
              <p className="text-xs font-mono text-arachne-muted uppercase tracking-widest">Global Configuration</p>
            </div>
          </div>

          <div className="bg-arachne-surface border border-arachne-border rounded-xl overflow-hidden">
            <table className="w-full text-left font-mono text-xs">
              <tbody className="divide-y divide-arachne-border/50">
                {[
                  { label: 'Concurrency', value: engine?.concurrency, icon: LuBoxes },
                  { label: 'Request Concurrency', value: engine?.request_concurrency, icon: LuZap },
                  { label: 'Network Timeout', value: engine?.timeout_seconds ? `${engine.timeout_seconds}s` : 'N/A', icon: LuClock },
                  { label: 'System Agent', value: engine?.user_agent, icon: LuTerminal },
                  { label: 'Storage Mode', value: 'SQLite Persistence', icon: LuDatabase },
                ].map((row) => (
                  <tr key={row.label} className="hover:bg-arachne-surface-alt transition-colors">
                    <td className="py-4 px-6 text-arachne-muted uppercase flex items-center gap-3">
                      <row.icon className="text-primary/50 text-sm" />
                      {row.label}
                    </td>
                    <td className="py-4 px-6 text-arachne-text font-bold truncate max-w-xs">{row.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};

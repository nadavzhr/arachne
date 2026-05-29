import { useAnalytics } from '../hooks/useAnalytics';
import { LuCircleCheck, LuCircleX, LuTriangleAlert, LuClock, LuSearch, LuFilter } from "react-icons/lu";

export const AnalyticsView = () => {
  const { data, isLoading, error } = useAnalytics();

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-arachne-muted animate-pulse uppercase tracking-widest text-xs">
        [ SIGNAL_TRACE ] RETRIEVING NETWORK HEALTH DATA...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-red-500 uppercase tracking-widest text-xs">
        [ SYSTEM_ERROR ] FAILED TO CONNECT TO ANALYTICS SERVICE
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto bg-grid p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-arachne-surface border border-arachne-border p-6 rounded-xl shadow-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 text-primary/10 group-hover:text-primary/20 transition-colors">
              <LuSearch className="text-4xl" />
            </div>
            <div className="text-xs font-mono text-arachne-muted uppercase tracking-[0.2em] mb-2">Total Crawled Data</div>
            <div className="text-5xl font-display font-bold text-arachne-text">{data?.total_jobs || 0} <span className="text-sm text-arachne-muted font-normal uppercase tracking-widest">Nodes</span></div>
          </div>
          
          <div className="bg-arachne-surface border border-arachne-border p-6 rounded-xl shadow-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 text-primary/10 group-hover:text-primary/20 transition-colors">
              <LuClock className="text-4xl" />
            </div>
            <div className="text-xs font-mono text-arachne-muted uppercase tracking-[0.2em] mb-2">Last System Pulse</div>
            <div className="text-3xl font-display font-bold text-arachne-text uppercase tracking-tight">
              {data?.last_updated ? new Date(data.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'N/A'}
            </div>
            <div className="text-xs text-arachne-muted mt-1 font-mono uppercase tracking-widest">
              {data?.last_updated ? new Date(data.last_updated).toLocaleDateString() : 'NO PULSE DETECTED'}
            </div>
          </div>

          <div className="bg-arachne-surface border border-arachne-border p-6 rounded-xl shadow-sm lg:col-span-1 sm:col-span-2 relative overflow-hidden group">
             <div className="absolute top-0 right-0 p-4 text-primary/10 group-hover:text-primary/20 transition-colors">
              <LuFilter className="text-4xl" />
            </div>
            <div className="text-xs font-mono text-arachne-muted uppercase tracking-[0.2em] mb-2">Active Spiders</div>
            <div className="text-5xl font-display font-bold text-arachne-text">{data?.spider_status?.length || 0}</div>
          </div>
        </div>

        {/* Spider Grid */}
        <div className="space-y-4">
          <h2 className="font-display font-bold text-xl tracking-tight flex items-center gap-2 uppercase">
            <div className="h-2 w-2 rounded-full bg-primary" />
            Spider Network Health
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.spider_status?.map((spider) => (
              <div key={spider.spider} className="bg-arachne-surface border border-arachne-border rounded-xl p-6 hover:border-primary/30 transition-all group">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className={`h-12 w-12 rounded-xl flex items-center justify-center border ${
                      spider.status === 'success' ? 'bg-green-500/10 border-green-500/20 text-green-500' :
                      spider.status === 'failed' ? 'bg-red-500/10 border-red-500/20 text-red-500' :
                      'bg-yellow-500/10 border-yellow-500/20 text-yellow-500'
                    }`}>
                      {spider.status === 'success' ? <LuCircleCheck className="text-2xl" /> :
                       spider.status === 'failed' ? <LuCircleX className="text-2xl" /> :
                       <LuTriangleAlert className="text-2xl" />}
                    </div>
                    <div>
                      <div className="font-display font-bold text-base uppercase tracking-wide group-hover:text-primary transition-colors">{spider.spider}</div>
                      <div className="text-xs font-mono text-arachne-muted uppercase tracking-tighter">PULSE: {new Date(spider.executed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6 py-4 border-t border-arachne-border/50">
                  <div>
                    <div className="text-[11px] font-mono text-arachne-muted uppercase flex items-center gap-1.5 mb-1 tracking-widest">
                      <LuSearch className="text-xs text-primary/50" /> Found
                    </div>
                    <div className="text-3xl font-display font-bold text-arachne-text">{spider.found_count}</div>
                  </div>
                  <div>
                    <div className="text-[11px] font-mono text-arachne-muted uppercase flex items-center gap-1.5 mb-1 tracking-widest">
                      <LuFilter className="text-xs text-primary/50" /> Filtered
                    </div>
                    <div className="text-3xl font-display font-bold text-arachne-text">{spider.filtered_count}</div>
                  </div>
                </div>

                {spider.error_message && (
                  <div className="mt-3 p-3 bg-red-500/5 border border-red-500/10 rounded-lg">
                    <div className="text-[9px] font-mono text-red-500 uppercase mb-1 tracking-tighter font-bold">Error Trace</div>
                    <div className="text-[10px] font-mono text-red-400/80 line-clamp-2 leading-relaxed italic">
                      {spider.error_message}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Distributions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 font-body">
          {/* Company Distribution */}
          <div className="space-y-4">
            <h2 className="font-display font-bold text-xl tracking-tight flex items-center gap-2 uppercase">
              <div className="h-2 w-2 rounded-full bg-primary" />
              Target Distribution
            </h2>
            <div className="bg-arachne-surface border border-arachne-border rounded-xl p-6 space-y-4">
              {data?.company_distribution?.slice(0, 6).map((company) => {
                const percentage = (company.count / data.total_jobs) * 100;
                return (
                  <div key={company.name} className="space-y-1.5">
                    <div className="flex justify-between text-[11px] font-mono tracking-widest">
                      <span className="text-arachne-text uppercase font-bold">{company.name}</span>
                      <span className="text-arachne-muted">{company.count} NODES</span>
                    </div>
                    <div className="h-2 bg-arachne-surface-alt rounded-full overflow-hidden border border-arachne-border/50">
                      <div 
                        className="h-full bg-primary transition-all duration-1000" 
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Log Feed */}
          <div className="space-y-4">
            <h2 className="font-display font-bold text-xl tracking-tight flex items-center gap-2 uppercase">
              <div className="h-2 w-2 rounded-full bg-primary" />
              System Log Stream
            </h2>
            <div className="bg-arachne-surface-alt border border-arachne-border rounded-xl p-4 font-mono text-[10px] space-y-2 h-[280px] overflow-auto custom-scrollbar">
              {data?.spider_status?.map((spider, i) => (
                <div key={i} className="flex gap-3 text-arachne-muted border-b border-arachne-border/30 pb-2 tracking-tighter leading-relaxed">
                  <span className="text-primary shrink-0">[{new Date(spider.executed_at).toLocaleTimeString()}]</span>
                  <span className="text-arachne-text shrink-0 uppercase font-bold">{spider.spider}:</span>
                  <span className="uppercase">
                    {spider.status === 'success' ? `SUCCESSFULLY SCANNED. FOUND ${spider.found_count} NODES.` :
                     spider.status === 'failed' ? `CRITICAL FAILURE: ${spider.error_message}` :
                     `PARTIAL SCAN COMPLETE. ${spider.found_count} NODES RETRIEVED.`}
                  </span>
                </div>
              ))}
              <div className="flex gap-3 text-green-500/50 tracking-widest text-[9px] font-bold">
                <span className="shrink-0 animate-pulse">&gt;</span>
                <span className="animate-pulse italic">LISTENING FOR NEXT PULSE... [ SECURE_FEED_ACTIVE ]</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

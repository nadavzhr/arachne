import { motion, type Variants } from 'framer-motion';
import { useAnalytics } from '../hooks/useAnalytics';
import { LuCircleCheck, LuCircleX, LuTriangleAlert, LuClock, LuSearch, LuFilter, LuActivity } from "react-icons/lu";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.4, ease: [0.25, 1, 0.5, 1] }
  }
};

export const AnalyticsView = () => {
  const { data, isLoading, error } = useAnalytics();

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col min-h-0 overflow-y-auto bg-grid p-4 md:p-8 h-full">
        <div className="max-w-6xl mx-auto space-y-8 w-full animate-pulse">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-arachne-surface-alt/50 border border-arachne-border rounded-2xl" />
            ))}
          </div>
          <div className="space-y-6">
            <div className="h-6 w-48 bg-arachne-surface-alt rounded-md" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-48 bg-arachne-surface-alt/50 border border-arachne-border rounded-2xl" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex-1 flex items-center justify-center font-mono text-primary uppercase tracking-widest text-xs">
        [ SYSTEM_ERROR ] FAILED_TO_CONNECT_TO_ANALYTICS_SERVICE
      </div>
    );
  }

  return (
    <motion.div 
      className="flex-1 flex flex-col min-h-0 overflow-y-auto bg-grid p-4 md:p-8 custom-scrollbar h-full"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="max-w-6xl mx-auto space-y-8 w-full">
        {/* Header Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <motion.div 
            variants={cardVariants}
            className="bg-arachne-surface border border-arachne-border p-8 rounded-2xl shadow-sm relative overflow-hidden group hover:border-primary/20 transition-all duration-300"
          >
            <div className="absolute top-0 right-0 p-4 text-primary/5 group-hover:text-primary/10 transition-colors">
              <LuSearch className="text-6xl" />
            </div>
            <div className="text-[10px] font-mono text-arachne-muted uppercase tracking-[0.2em] mb-4 font-bold flex items-center gap-2">
              <div className="h-1 w-1 rounded-full bg-primary" />
              Total Nodes Indexed
            </div>
            <div className="text-6xl font-display font-bold text-arachne-text flex items-baseline gap-3">
              <span style={{ fontVariantNumeric: 'tabular-nums' }}>{data?.total_jobs || 0}</span>
              <span className="text-xs text-arachne-muted font-mono uppercase tracking-widest font-normal">Active_Threads</span>
            </div>
          </motion.div>
          
          <motion.div 
            variants={cardVariants}
            className="bg-arachne-surface border border-arachne-border p-8 rounded-2xl shadow-sm relative overflow-hidden group hover:border-primary/20 transition-all duration-300"
          >
            <div className="absolute top-0 right-0 p-4 text-primary/5 group-hover:text-primary/10 transition-colors">
              <LuClock className="text-6xl" />
            </div>
            <div className="text-[10px] font-mono text-arachne-muted uppercase tracking-[0.2em] mb-4 font-bold flex items-center gap-2">
              <div className="h-1 w-1 rounded-full bg-primary" />
              Last System Pulse
            </div>
            <div className="text-3xl font-display font-bold text-arachne-text uppercase tracking-tight">
              {data?.last_updated ? new Date(data.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'N/A'}
            </div>
            <div className="text-[10px] text-arachne-muted mt-3 font-mono uppercase tracking-widest border-t border-arachne-border/50 pt-3 flex justify-between">
              <span>{data?.last_updated ? new Date(data.last_updated).toLocaleDateString() : 'NO PULSE DETECTED'}</span>
              <span className="text-primary/60">READY</span>
            </div>
          </motion.div>

          <motion.div 
            variants={cardVariants}
            className="bg-arachne-surface border border-arachne-border p-8 rounded-2xl shadow-sm lg:col-span-1 sm:col-span-2 relative overflow-hidden group hover:border-primary/20 transition-all duration-300"
          >
             <div className="absolute top-0 right-0 p-4 text-primary/5 group-hover:text-primary/10 transition-colors">
              <LuFilter className="text-6xl" />
            </div>
            <div className="text-[10px] font-mono text-arachne-muted uppercase tracking-[0.2em] mb-4 font-bold flex items-center gap-2">
              <div className="h-1 w-1 rounded-full bg-primary" />
              Active Spiders
            </div>
            <div className="text-6xl font-display font-bold text-arachne-text" style={{ fontVariantNumeric: 'tabular-nums' }}>
              {data?.spider_status?.length || 0}
            </div>
          </motion.div>
        </div>

        {/* Spider Grid */}
        <div className="space-y-6">
          <h2 className="font-display font-bold text-xl tracking-tight flex items-center gap-3 uppercase">
            <LuActivity className="text-primary" />
            Spider Network Health
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.spider_status?.map((spider) => (
              <motion.div 
                key={spider.spider} 
                variants={cardVariants}
                className="bg-arachne-surface border border-arachne-border rounded-2xl p-6 hover:border-primary/40 transition-all group relative overflow-hidden shadow-sm"
              >
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className={`h-14 w-14 rounded-xl flex items-center justify-center border transition-all duration-500 group-hover:scale-105 ${
                      spider.status === 'success' ? 'bg-green-500/5 border-green-500/20 text-green-500 shadow-[0_0_15px_rgba(34,197,94,0.1)]' :
                      spider.status === 'failed' ? 'bg-red-500/5 border-red-500/20 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.1)]' :
                      'bg-yellow-500/5 border-yellow-500/20 text-yellow-500'
                    }`}>
                      {spider.status === 'success' ? <LuCircleCheck className="text-2xl" /> :
                       spider.status === 'failed' ? <LuCircleX className="text-2xl" /> :
                       <LuTriangleAlert className="text-2xl" />}
                    </div>
                    <div>
                      <div className="font-display font-bold text-lg uppercase tracking-wide group-hover:text-primary transition-colors">{spider.spider}</div>
                      <div className="text-[10px] font-mono text-arachne-muted uppercase tracking-tighter">PULSE: {new Date(spider.executed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6 py-4 border-t border-arachne-border/50">
                  <div>
                    <div className="text-[10px] font-mono text-arachne-muted uppercase flex items-center gap-1.5 mb-1 tracking-widest font-bold">
                      Found
                    </div>
                    <div className="text-3xl font-display font-bold text-arachne-text" style={{ fontVariantNumeric: 'tabular-nums' }}>{spider.found_count}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-mono text-arachne-muted uppercase flex items-center gap-1.5 mb-1 tracking-widest font-bold">
                      Filtered
                    </div>
                    <div className="text-3xl font-display font-bold text-arachne-text" style={{ fontVariantNumeric: 'tabular-nums' }}>{spider.filtered_count}</div>
                  </div>
                </div>

                {spider.error_message && (
                  <div className="mt-4 p-4 bg-red-500/5 border border-red-500/10 rounded-xl">
                    <div className="text-[9px] font-mono text-red-500 uppercase mb-2 tracking-tighter font-bold flex items-center gap-2">
                      <LuTriangleAlert className="text-xs" />
                      Error Trace
                    </div>
                    <div className="text-[11px] font-mono text-red-400/90 line-clamp-3 leading-relaxed italic">
                      {spider.error_message}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* Distributions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 font-body">
          <motion.div variants={cardVariants} className="space-y-6">
            <h2 className="font-display font-bold text-xl tracking-tight flex items-center gap-3 uppercase">
              <div className="h-1.5 w-1.5 rounded-full bg-primary" />
              Target Distribution
            </h2>
            <div className="bg-arachne-surface border border-arachne-border rounded-2xl p-8 space-y-6 shadow-sm">
              {data?.company_distribution?.slice(0, 6).map((company) => {
                const percentage = (company.count / data.total_jobs) * 100;
                return (
                  <div key={company.name} className="space-y-3">
                    <div className="flex justify-between text-xs font-mono tracking-widest">
                      <span className="text-arachne-text uppercase font-bold">{company.name}</span>
                      <span className="text-arachne-muted" style={{ fontVariantNumeric: 'tabular-nums' }}>{company.count} NODES</span>
                    </div>
                    <div className="h-2 bg-arachne-bg rounded-full overflow-hidden border border-arachne-border/30">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 1, ease: "easeOut", delay: 0.5 }}
                        className="h-full bg-primary shadow-[0_0_12px_rgba(219,44,31,0.4)]" 
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>

          <motion.div variants={cardVariants} className="space-y-6">
            <h2 className="font-display font-bold text-xl tracking-tight flex items-center gap-3 uppercase">
              <div className="h-1.5 w-1.5 rounded-full bg-primary" />
              System Log Stream
            </h2>
            <div className="bg-arachne-surface-alt/40 border border-arachne-border rounded-2xl p-6 font-mono text-[11px] space-y-4 h-[350px] overflow-auto custom-scrollbar shadow-inner">
              {data?.spider_status?.map((spider, i) => (
                <div key={i} className="flex gap-4 text-arachne-muted border-b border-arachne-border/20 pb-3 tracking-tighter leading-relaxed hover:text-arachne-text transition-colors group">
                  <span className="text-primary shrink-0 font-bold">[{new Date(spider.executed_at).toLocaleTimeString()}]</span>
                  <span className="text-arachne-text shrink-0 uppercase font-bold group-hover:text-primary transition-colors">{spider.spider}:</span>
                  <span className="uppercase opacity-80 group-hover:opacity-100">
                    {spider.status === 'success' ? `Successfully scanned sector. Retrieved ${spider.found_count} nodes.` :
                     spider.status === 'failed' ? `Sector compromise detected: ${spider.error_message}` :
                     `Partial data retrieved. ${spider.found_count} nodes synchronized.`}
                  </span>
                </div>
              ))}
              <div className="flex gap-3 text-green-500/50 tracking-widest text-[10px] font-bold py-4">
                <span className="shrink-0 animate-pulse">&gt;</span>
                <span className="animate-pulse italic">LISTENING_FOR_NEXT_PULSE... [ SECURE_FEED_ACTIVE ]</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

import { LuLayoutGrid, LuActivity, LuSettings, LuShieldCheck } from "react-icons/lu";

export type ViewType = 'jobs' | 'analytics' | 'system';

interface SidebarProps {
  activeView: ViewType;
  setActiveView: (view: ViewType) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar = ({ activeView, setActiveView, isOpen, onClose }: SidebarProps) => {
  const menuItems = [
    { id: 'jobs' as ViewType, label: 'Jobs', icon: LuLayoutGrid },
    { id: 'analytics' as ViewType, label: 'Analytics', icon: LuActivity },
    { id: 'system' as ViewType, label: 'System', icon: LuSettings },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-md"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 md:w-20 lg:w-64
        bg-arachne-surface border-r border-arachne-border
        transition-all duration-300 ease-in-out
        ${isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full md:translate-x-0'}
        flex flex-col
      `}>
        <nav className="flex-1 py-8 px-4 flex flex-col gap-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveView(item.id);
                  onClose();
                }}
                className={`
                  flex items-center gap-4 p-4 rounded-2xl transition-all group relative overflow-hidden
                  ${isActive 
                    ? 'bg-primary/10 text-primary border border-primary/20' 
                    : 'text-arachne-muted hover:bg-arachne-surface-alt hover:text-arachne-text border border-transparent'}
                `}
                title={item.label}
              >
                {/* Active Signal Stripe */}
                <div className={`
                  absolute left-0 top-0 bottom-0 w-[3px] bg-primary transition-transform duration-300 origin-left
                  ${isActive ? 'scale-y-100' : 'scale-y-0 group-hover:scale-y-100'}
                `} />

                <Icon className={`text-xl shrink-0 transition-colors ${isActive ? 'text-primary' : 'group-hover:text-primary'}`} />
                <span className="font-display font-bold text-sm md:hidden lg:block uppercase tracking-wider">
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-arachne-border md:hidden lg:block">
          <div className="bg-arachne-surface-alt/50 p-5 rounded-2xl border border-arachne-border relative overflow-hidden group">
            <div className="flex items-center gap-2 mb-3">
              <LuShieldCheck className="text-primary text-sm animate-pulse" />
              <span className="text-[10px] font-mono text-arachne-muted uppercase tracking-[0.2em] font-bold">System Status</span>
            </div>
            <div className="h-1 w-full bg-arachne-bg rounded-full overflow-hidden mb-3">
              <div className="h-full bg-green-500 w-full animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.4)]" />
            </div>
            <div className="text-[10px] font-mono text-arachne-muted/80 leading-relaxed uppercase tracking-tighter">
              v0.1 // SECURE_FEED<br />
              ESTABLISHED: <span className="text-green-500 font-bold">OK</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

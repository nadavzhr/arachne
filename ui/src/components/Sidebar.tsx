import { LuLayoutGrid, LuActivity, LuSettings } from "react-icons/lu";

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
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 md:w-16 lg:w-64
        bg-arachne-surface border-r border-arachne-border
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        flex flex-col
      `}>
        <nav className="flex-1 py-4 px-3 flex flex-col gap-2">
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
                  flex items-center gap-4 p-3 rounded-lg transition-all group
                  ${isActive 
                    ? 'bg-primary/10 text-primary border border-primary/20' 
                    : 'text-arachne-muted hover:bg-arachne-surface-alt hover:text-arachne-text border border-transparent'}
                `}
                title={item.label}
              >
                <Icon className={`text-xl shrink-0 ${isActive ? 'text-primary' : 'group-hover:text-primary'}`} />
                <span className="font-display font-medium text-sm md:hidden lg:block">
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t border-arachne-border md:hidden lg:block">
          <div className="bg-arachne-surface-alt p-3 rounded-lg border border-arachne-border">
            <div className="flex items-center gap-2 mb-1">
              <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] font-mono text-arachne-muted uppercase tracking-wider">System Live</span>
            </div>
            <div className="text-[9px] font-mono text-arachne-muted/70 leading-tight">
              ARACHNE JOB WEAVER v0.1<br />
              SECURE FEED ACTIVE
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

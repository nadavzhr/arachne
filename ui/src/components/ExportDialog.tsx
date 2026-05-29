import { LuFileJson, LuFileSpreadsheet, LuX } from "react-icons/lu";

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (format: 'json' | 'csv') => void;
}

export const ExportDialog = ({ isOpen, onClose, onExport }: ExportDialogProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      <div className="relative bg-arachne-surface border border-arachne-border rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="p-6 border-b border-arachne-border flex items-center justify-between">
          <div>
            <h3 className="font-display font-bold text-lg uppercase tracking-tight text-arachne-text">Export Intelligence</h3>
            <p className="text-[10px] font-mono text-arachne-muted uppercase tracking-widest">Select Output Protocol</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-arachne-surface-alt rounded-full transition-colors text-arachne-muted hover:text-arachne-text"
          >
            <LuX className="text-xl" />
          </button>
        </div>

        <div className="p-6 grid grid-cols-2 gap-4">
          <button
            onClick={() => {
              onExport('json');
              onClose();
            }}
            className="flex flex-col items-center gap-3 p-6 bg-arachne-surface-alt border border-arachne-border rounded-xl hover:border-primary/50 hover:bg-primary/5 transition-all group"
          >
            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
              <LuFileJson className="text-2xl" />
            </div>
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-arachne-muted group-hover:text-primary">JSON</span>
          </button>

          <button
            onClick={() => {
              onExport('csv');
              onClose();
            }}
            className="flex flex-col items-center gap-3 p-6 bg-arachne-surface-alt border border-arachne-border rounded-xl hover:border-primary/50 hover:bg-primary/5 transition-all group"
          >
            <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center text-green-500 group-hover:scale-110 transition-transform">
              <LuFileSpreadsheet className="text-2xl" />
            </div>
            <span className="font-mono text-xs font-bold uppercase tracking-wider text-arachne-muted group-hover:text-green-500">CSV</span>
          </button>
        </div>

        <div className="px-6 py-4 bg-arachne-surface-alt border-t border-arachne-border flex justify-end">
          <button 
            onClick={onClose}
            className="text-[11px] font-mono uppercase tracking-widest text-arachne-muted hover:text-arachne-text transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

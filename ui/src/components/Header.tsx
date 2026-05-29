import React from 'react';
import { LuGithub, LuMenu, LuSun, LuMoon, LuDownload } from 'react-icons/lu';
import logo from '../assets/arachne-logo.png';

interface HeaderProps {
  theme: 'light' | 'dark';
  setTheme: React.Dispatch<React.SetStateAction<'light' | 'dark'>>;
  exportToJson: () => void;
  toggleSidebar: () => void;
}

export const Header = ({ theme, setTheme, exportToJson, toggleSidebar }: HeaderProps) => {
  return (
    <header className="border-b border-arachne-border bg-arachne-surface px-4 md:px-8 h-16 flex items-center justify-between shrink-0 relative z-10 w-full">
      <div className="flex items-center gap-3">
        <button 
          onClick={toggleSidebar}
          className="md:hidden p-2 -ml-2 text-arachne-muted hover:text-primary transition-colors"
          aria-label="Toggle menu"
        >
          <LuMenu className="text-xl" />
        </button>
        <img src={logo} alt="Arachne" className="h-8 w-8" />
        <div className="flex flex-col">
          <span className="font-display font-bold text-sm leading-none">ARACHNE</span>
          <span className="text-[10px] text-arachne-muted font-mono tracking-tighter">JOB WEAVER v0.1</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <a
          href="https://github.com/nadavzhr/arachne"
          target="_blank"
          rel="noreferrer"
          className="h-9 w-9 border border-arachne-border bg-arachne-surface-alt text-arachne-text hover:border-primary hover:text-primary transition-colors flex items-center justify-center rounded-lg"
          aria-label="View on GitHub"
        >
          <LuGithub className="text-lg" />
        </a>
        <button
          type="button"
          onClick={() => setTheme(prev => prev === 'dark' ? 'light' : 'dark')}
          className="h-9 w-9 border border-arachne-border bg-arachne-surface-alt text-arachne-text hover:border-primary hover:text-primary transition-colors flex items-center justify-center rounded-lg"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <LuSun className="text-lg" /> : <LuMoon className="text-lg" />}
        </button>
        <button
          onClick={exportToJson}
          className="h-9 bg-primary text-white font-bold text-[11px] uppercase tracking-widest px-4 hover:brightness-110 transition-all border border-primary flex items-center justify-center gap-2 rounded-lg ml-2"
        >
          <LuDownload className="text-sm" />
          <span className="hidden sm:inline">Export</span>
        </button>
      </div>
    </header>
  );
};

import { FaAmazon, FaApple, FaGoogle, FaMeta, FaMicrosoft } from 'react-icons/fa6';
import { SiNvidia } from 'react-icons/si';

interface CompanyLogoProps {
  company: string | null;
}

export const CompanyLogo = ({ company }: CompanyLogoProps) => {
  const iconClass = 'w-5 h-5 md:w-6 md:h-6 shrink-0';
  if (!company) {
    return (
      <div
        className={`${iconClass} flex items-center justify-center rounded-sm bg-arachne-surface-alt text-arachne-muted text-[10px]`}
      >
        ?
      </div>
    );
  }
  const c = company.toLowerCase();
  if (c.includes('meta')) return <FaMeta className={`${iconClass} text-[#0668E1]`} />;
  if (c.includes('google')) return <FaGoogle className={`${iconClass} text-[#EA4335]`} />;
  if (c.includes('amazon')) return <FaAmazon className={`${iconClass} text-[#FF9900]`} />;
  if (c.includes('microsoft')) return <FaMicrosoft className={`${iconClass} text-[#00A4EF]`} />;
  if (c.includes('nvidia')) return <SiNvidia className={`${iconClass} text-[#76B900]`} />;
  if (c.includes('apple')) return <FaApple className={`${iconClass} text-[#9AA0A6]`} />;
  return (
    <div
      className={`${iconClass} flex items-center justify-center rounded-sm bg-arachne-muted/20 text-arachne-text text-[10px]`}
    >
      {company.charAt(0)}
    </div>
  );
};

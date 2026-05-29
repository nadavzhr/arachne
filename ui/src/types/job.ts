export interface JobPosting {
  spider: string;
  company: string | null;
  title: string;
  url: string;
  location: string | null;
  external_id: string | null;
  posted_at: string | null;
  description: string | null;
  remote: boolean;
  employment_type: string | null;
  experience_level: string | null;
}

export interface SpiderStatus {
  id: number;
  spider: string;
  status: 'success' | 'failed' | 'partial_failure';
  found_count: number;
  filtered_count: number;
  error_message: string | null;
  executed_at: string;
}

export interface DistributionItem {
  name: string;
  count: number;
}

export interface AnalyticsData {
  last_updated: string;
  total_jobs: number;
  spider_status: SpiderStatus[];
  company_distribution: DistributionItem[];
  spider_distribution: DistributionItem[];
}

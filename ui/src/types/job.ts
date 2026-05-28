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

import { useEffect, useState } from 'react';
import type { JobPosting } from '../types/job';

export function useJobs() {
  const [data, setData] = useState<JobPosting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const baseUrl = import.meta.env.BASE_URL || '/';
        const response = await fetch(`${baseUrl}jobs.json`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Failed to load jobs.json (${response.status})`);
        }
        const payload = await response.json();
        if (isMounted) {
          setData(Array.isArray(payload) ? payload : []);
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          return;
        }
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    load();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  return { data, isLoading, error };
}

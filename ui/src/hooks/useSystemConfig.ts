import { useEffect, useState } from 'react';

export interface SystemConfigData {
  engine: {
    concurrency: number;
    request_concurrency: number;
    timeout_seconds: number;
    user_agent: string;
    data_dir: string;
  };
  profile: {
    name: string;
    search: {
      title: string;
      locations: string[];
    };
    filters: Record<string, {
      include_keywords: string[];
      exclude_keywords: string[];
    }>;
  };
}

export function useSystemConfig() {
  const [data, setData] = useState<SystemConfigData | null>(null);
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
        const response = await fetch(`${baseUrl}system_config.json`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Failed to load system_config.json (${response.status})`);
        }
        const payload = await response.json();
        if (isMounted) {
          setData(payload);
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

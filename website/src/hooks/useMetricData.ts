import { useEffect, useState } from "react";
import type { MetricData } from "../types";

declare const __R2_PUBLIC_URL__: string;

export function useMetricData( metric: string) {
  const [data, setData] = useState<MetricData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const url = `${__R2_PUBLIC_URL__}/${metric}.json`;
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`${res.status} fetching ${url}`);
        return res.json() as Promise<MetricData>;
      })
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, [metric]);

  return { data, loading, error };
}

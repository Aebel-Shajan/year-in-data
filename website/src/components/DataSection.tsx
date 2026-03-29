/**
 * One data section: title + heatmap + stats.
 * Year selection is controlled by the parent (App navbar).
 */

import { useEffect, useMemo } from "react";
import { useMetricData } from "../hooks/useMetricData";
import type { MetricConfig } from "../types";
import { Heatmap } from "./Heatmap";

interface Props {
  config: MetricConfig;
  year: number;
  onYearsLoaded: (years: number[]) => void;
}

export function DataSection({ config, year, onYearsLoaded }: Props) {
  const { source, metric, label, colorScheme } = config;
  const { data, loading, error } = useMetricData(source, metric);

  useEffect(() => {
    if (!data) return;
    const years = [...new Set(data.data.map((d) => parseInt(d.date.slice(0, 4))))].sort((a, b) => b - a);
    if (years.length > 0) onYearsLoaded(years);
  }, [data, onYearsLoaded]);

  const yearData = useMemo(
    () => data?.data.filter((d) => d.date.startsWith(String(year))) ?? [],
    [data, year]
  );

  const total = useMemo(() => yearData.reduce((s, d) => s + d.value, 0), [yearData]);
  const activeDays = useMemo(() => new Set(yearData.map((d) => d.date)).size, [yearData]);

  return (
    <section className="mb-12">
      <div className="flex items-baseline gap-4 mb-3">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{label}</h2>

        {data && (
          <span className="ml-auto text-sm text-gray-400">
            {activeDays} active days · {formatValue(total, data.unit)} total
          </span>
        )}
      </div>

      {loading && <SkeletonHeatmap />}
      {error && <p className="text-sm text-red-400">Failed to load: {error}</p>}
      {data && !loading && (
        <Heatmap
          data={data.data}
          year={year}
          colorScheme={colorScheme}
        />
      )}
    </section>
  );
}

function formatValue(v: number, unit: string): string {
  const rounded = Math.round(v).toLocaleString();
  return `${rounded} ${unit}`;
}

function SkeletonHeatmap() {
  return (
    <div className="w-full max-w-4xl h-24 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
  );
}

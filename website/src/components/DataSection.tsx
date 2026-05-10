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
  const { metric, colorScheme } = config;
  const { data, loading, error } = useMetricData(metric);

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
        {data
          ? <h2 className="text-base md:text-lg font-semibold text-gray-900 dark:text-gray-100">{data.label}</h2>
          : <div className="h-6 w-36 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
        }
        {data && (
          <span className="ml-auto text-xs md:text-sm text-gray-400 whitespace-nowrap">
            {activeDays} active days · {formatValue(total, data.unit)} total
          </span>
        )}
      </div>

      {loading && <SkeletonHeatmap />}
      {!loading && (
        <>
          {error && <p className="text-sm text-red-400 mb-2">Failed to load: {error}</p>}
          <Heatmap
            data={data?.data ?? []}
            year={year}
            colorScheme={colorScheme}
            unit={data?.unit}
          />
        </>
      )}
    </section>
  );
}

function formatValue(v: number, unit: string): string {
  if (unit === "minutes" && v >= 60) {
    const h = Math.floor(v / 60);
    const m = Math.round(v % 60);
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  }
  return `${Math.round(v).toLocaleString()} ${unit}`;
}

function SkeletonHeatmap() {
  return (
    <div className="w-full max-w-4xl h-24 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
  );
}

/**
 * SVG annual heatmap — same visual language as GitHub's contribution graph.
 *
 * Renders 52 columns (weeks) × 7 rows (Mon–Sun).
 * Each cell is coloured by value intensity using a d3 colour scale.
 */

import { scaleSequential } from "d3-scale";
import {
  interpolateBlues,
  interpolateGreens,
  interpolateOranges,
  interpolatePurples,
  interpolateReds,
  interpolateWarm,
} from "d3-scale-chromatic";
import React, { useMemo, useState } from "react";
import type { DataPoint } from "../types";

const INTERPOLATORS = {
  greens: interpolateGreens,
  blues: interpolateBlues,
  oranges: interpolateOranges,
  purples: interpolatePurples,
  reds: interpolateReds,
  warm: interpolateWarm,
} as const;

type ColorScheme = keyof typeof INTERPOLATORS;

interface Props {
  data: DataPoint[];
  year: number;
  colorScheme?: ColorScheme;
  unit?: string;
  cellSize?: number;
  gap?: number;
}

interface TooltipState {
  visible: boolean;
  x: number;
  y: number;
  date: string;
  value: number;
  label?: string;
}

// Day index: Monday = 0 … Sunday = 6  (ISO weekday - 1)
function isoWeekday(d: Date): number {
  return (d.getDay() + 6) % 7;
}

// Zero-indexed week within the year (Mon of first partial week = 0)
function weekIndex(d: Date, yearStart: Date): number {
  // Use Date.UTC to count calendar days, avoiding DST offsets from getTime()
  const utcDays = (Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())
    - Date.UTC(yearStart.getFullYear(), yearStart.getMonth(), yearStart.getDate())) / 86_400_000;
  return Math.floor((utcDays + isoWeekday(yearStart)) / 7);
}

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", "Sun"];

function formatMinutes(v: number): string {
  if (v >= 60) {
    const h = Math.floor(v / 60);
    const m = Math.round(v % 60);
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  }
  return `${Math.round(v)}m`;
}

export function Heatmap({ data, year, colorScheme = "greens", unit, cellSize = 13, gap = 2 }: Props) {
  const step = cellSize + gap;

  const [tooltip, setTooltip] = useState<TooltipState>({ visible: false, x: 0, y: 0, date: "", value: 0 });

  const byDate = useMemo(() => {
    const map = new Map<string, number>();
    for (const d of data) {
      if (d.date.startsWith(String(year))) {
        map.set(d.date, (map.get(d.date) ?? 0) + d.value);
      }
    }
    return map;
  }, [data, year]);

  const maxValue = useMemo(() => Math.max(...byDate.values(), 1), [byDate]);

  const colorScale = useMemo(
    () => scaleSequential(INTERPOLATORS[colorScheme]).domain([0, maxValue]),
    [colorScheme, maxValue]
  );

  // Build the grid: 53 possible week columns × 7 day rows
  const yearStart = new Date(year, 0, 1);
  const yearEnd = new Date(year, 11, 31);
  const totalWeeks = weekIndex(yearEnd, yearStart) + 1;

  // Month label positions (first day of each month → column)
  const monthPositions = useMemo(() => {
    const positions: { label: string; col: number }[] = [];
    for (let m = 0; m < 12; m++) {
      const d = new Date(year, m, 1);
      const col = weekIndex(d, yearStart);
      if (positions.length === 0 || positions[positions.length - 1].col !== col) {
        positions.push({ label: MONTH_LABELS[m], col });
      }
    }
    return positions;
  }, [year, yearStart]);

  const weeklyTotals = useMemo(() => {
    const totals = new Map<number, number>();
    const start = new Date(year, 0, 1);
    for (const [dateStr, value] of byDate) {
      const col = weekIndex(new Date(dateStr + "T00:00:00"), start);
      totals.set(col, (totals.get(col) ?? 0) + value);
    }
    return totals;
  }, [byDate, year]);

  const maxWeekly = useMemo(() => Math.max(...weeklyTotals.values(), 1), [weeklyTotals]);

  const paddingLeft = 28; // space for day labels
  const paddingTop = 20;  // space for month labels
  const BAR_MAX_H = 30;
  const BAR_GAP = 4;
  const gridBottom = paddingTop + 7 * step;
  const svgWidth = paddingLeft + totalWeeks * step + gap;
  const svgHeight = gridBottom + BAR_GAP + BAR_MAX_H + gap;

  const cells: React.ReactNode[] = [];
  let cursor = new Date(yearStart);
  while (cursor <= yearEnd) {
    const iso = `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}-${String(cursor.getDate()).padStart(2, "0")}`;
    const value = byDate.get(iso) ?? 0;
    const col = weekIndex(cursor, yearStart);
    const row = isoWeekday(cursor);

    cells.push(
      <rect
        key={iso}
        x={paddingLeft + col * step}
        y={paddingTop + row * step}
        width={cellSize}
        height={cellSize}
        rx={2}
        // Use inline style for colored cells so it beats CSS specificity;
        // leave style unset for empty cells so Tailwind dark: classes apply.
        style={value > 0 ? { fill: colorScale(value) } : undefined}
        className={value === 0 ? "fill-gray-200 dark:fill-gray-700" : undefined}
        onMouseEnter={(e) => setTooltip({ visible: true, x: e.clientX, y: e.clientY, date: iso, value })}
        onMouseMove={(e) => setTooltip((t) => ({ ...t, x: e.clientX, y: e.clientY }))}
        onMouseLeave={() => setTooltip((t) => ({ ...t, visible: false }))}
      />
    );

    cursor.setDate(cursor.getDate() + 1);
  }

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="w-full max-w-3xl"
        aria-label={`${year} activity heatmap`}
      >
        {/* Month labels */}
        {monthPositions.map(({ label, col }) => (
          <text
            key={label}
            x={paddingLeft + col * step}
            y={paddingTop - 4}
            fontSize={10}
            fill="currentColor"
            className="fill-gray-500"
          >
            {label}
          </text>
        ))}

        {/* Day-of-week labels */}
        {DAY_LABELS.map((label, i) =>
          label ? (
            <text
              key={i}
              x={paddingLeft - 4}
              y={paddingTop + i * step + cellSize - 2}
              fontSize={9}
              textAnchor="end"
              fill="currentColor"
              className="fill-gray-400"
            >
              {label}
            </text>
          ) : null
        )}

        {/* Cells */}
        {cells}

        {/* Weekly total bars */}
        {Array.from(weeklyTotals.entries()).map(([col, total]) => {
          const barH = Math.max(1, (total / maxWeekly) * BAR_MAX_H);
          const weekStart = new Date(yearStart);
          weekStart.setDate(weekStart.getDate() + col * 7 - isoWeekday(yearStart));
          if (weekStart < yearStart) weekStart.setTime(yearStart.getTime());
          const weekLabel = `Week of ${weekStart.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
          const handlers = {
            onMouseEnter: (e: React.MouseEvent) => setTooltip({ visible: true, x: e.clientX, y: e.clientY, date: weekLabel, value: total, label: "weekly total" }),
            onMouseMove:  (e: React.MouseEvent) => setTooltip((t) => ({ ...t, x: e.clientX, y: e.clientY })),
            onMouseLeave: () => setTooltip((t) => ({ ...t, visible: false })),
          };
          return (
            <g key={`bar-${col}`}>
              <rect
                x={paddingLeft + col * step}
                y={gridBottom + BAR_GAP + (BAR_MAX_H - barH)}
                width={cellSize}
                height={barH}
                rx={1}
                style={{ fill: colorScale(total / 7) }}
                opacity={0.75}
              />
              {/* full-height invisible hit target */}
              <rect
                x={paddingLeft + col * step}
                y={gridBottom + BAR_GAP}
                width={cellSize}
                height={BAR_MAX_H}
                fill="transparent"
                {...handlers}
              />
            </g>
          );
        })}
      </svg>

      {tooltip.visible && (
        <div
          className="fixed z-50 pointer-events-none px-2 py-1 rounded shadow text-xs
                     bg-gray-900 text-white dark:bg-gray-700"
          style={{ left: tooltip.x + 12, top: tooltip.y - 32 }}
        >
          <span className="text-gray-400">{tooltip.date}</span>
          <span className="ml-2 font-semibold">
            {unit === "minutes" ? formatMinutes(tooltip.value) : tooltip.value.toLocaleString()}
          </span>
          {tooltip.label && <span className="ml-1 text-gray-400">({tooltip.label})</span>}
        </div>
      )}
    </div>
  );
}

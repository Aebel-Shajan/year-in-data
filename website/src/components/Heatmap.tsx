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
import React, { useMemo } from "react";
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
  cellSize?: number;
  gap?: number;
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

export function Heatmap({ data, year, colorScheme = "greens", cellSize = 13, gap = 2 }: Props) {
  const step = cellSize + gap;

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

  const paddingLeft = 28; // space for day labels
  const paddingTop = 20;  // space for month labels
  const svgWidth = paddingLeft + totalWeeks * step + gap;
  const svgHeight = paddingTop + 7 * step + gap;

  const cells: React.ReactNode[] = [];
  let cursor = new Date(yearStart);
  while (cursor <= yearEnd) {
    const iso = `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}-${String(cursor.getDate()).padStart(2, "0")}`;
    const value = byDate.get(iso) ?? 0;
    const col = weekIndex(cursor, yearStart);
    const row = isoWeekday(cursor);
    const fill = value > 0 ? colorScale(value) : "#ebedf0";

    cells.push(
      <rect
        key={iso}
        x={paddingLeft + col * step}
        y={paddingTop + row * step}
        width={cellSize}
        height={cellSize}
        rx={2}
        fill={fill}
        data-date={iso}
        data-value={value}
      >
        <title>{`${iso}: ${value.toLocaleString()}`}</title>
      </rect>
    );

    cursor.setDate(cursor.getDate() + 1);
  }

  return (
    <svg
      viewBox={`0 0 ${svgWidth} ${svgHeight}`}
      className="w-full max-w-4xl"
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
    </svg>
  );
}

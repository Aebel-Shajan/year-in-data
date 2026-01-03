import _ from "lodash";
import { useEffect, useState } from "react";

// Types
const DEFAULT_HEATMAP_SETTINGS: HeatmapSettings = {
  radius: 7,
  daySpacing: 2,
  monthSpacing: 20,
  xOffset: 0,
  yOffset: 0,
}

export type HeatmapDataType = { [x: string]: number; }

export interface HeatmapSettings {
  radius: number,
  daySpacing: number,
  monthSpacing: number,
  xOffset: number,
  yOffset: number,
}

// Utils
function getCSSVariable(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function constructDurationString(timeInSeconds: number): string {
  const hours = Math.floor(timeInSeconds / 3600)
  const minutes = Math.floor((timeInSeconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

function getAllUTCdatesInYear(year: number): Date[] {
  const dates: Date[] = [];
  const start = Date.UTC(year, 0, 1);       // Jan 1 UTC midnight
  const end = Date.UTC(year + 1, 0, 1);     // Jan 1 next year UTC midnight

  for (let time = start; time < end; time += 24 * 60 * 60 * 1000) {
    dates.push(new Date(time)); // each is a UTC date
  }

  return dates;
}

function getMonthNames(locale = "en-US", format: "long" | "short" = "long"): string[] {
  return Array.from({ length: 12 }, (_, i) =>
    new Date(2000, i, 1).toLocaleString(locale, { month: format })
  );
}

function getUTCDateOnly(dateStr: string): Date {
  const date = new Date(dateStr);
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}

function getWeekNumber(date: Date): number {
  const firstDay = new Date(date.getFullYear(), 0, 1);
  const pastDays = Math.floor((+date - +firstDay) / (24 * 60 * 60 * 1000));
  return Math.ceil((pastDays + firstDay.getDay() + 1) / 7) - 1;
};

function getHeatmapPosition(
  dayNumber: number,
  monthNumber: number,
  weekNumber: number,
  heatmapSettings: HeatmapSettings,
) {
  const { radius, daySpacing, monthSpacing, xOffset, yOffset } = heatmapSettings
  const multiplier = (2 * radius) + daySpacing
  const totalXOffset = radius + xOffset
  const totalYOffset = radius + yOffset

  const xPos = totalXOffset + (weekNumber * multiplier) + (monthSpacing * monthNumber)
  const yPos = totalYOffset + dayNumber * multiplier
  return {
    xPos,
    yPos
  }
}



function getColorFromValue(
  value: number,
  min: number,
  max: number,
  // palette: string[]
): string {
  const palette = [
    "#357A4F", // forest/muted green (low intensity)
    "#53A36D", // mid pastel green
    "#7FD699", // bright mint green
    "#D2F3D4"  // soft pale mint highlight
  ];
  const clamped = Math.min(Math.max(value, min), max);
  const ratio = (clamped - min) / (max - min);
  const index = Math.floor(ratio * (palette.length - 1));
  return palette[index];
}


// Components
function DayCircleCell(
  {
    date,
    value,
    heatmapSettings = DEFAULT_HEATMAP_SETTINGS
  }: {
    date: Date,
    value: number,
    heatmapSettings?: HeatmapSettings
  }
) {
  const heatmapPos = getHeatmapPosition(
    date.getUTCDay(),
    date.getUTCMonth(),
    getWeekNumber(date),
    heatmapSettings
  )

  return (
    <g
      key={date.toDateString()}
      className="group transition-all duration-150 cursor-pointer"
    >
      {/* Circle */}
      <circle
        className="
      transition-all duration-150 
      hover:stroke-white hover:stroke-[2px]
    "
        fill={
          value > 0
            ? getColorFromValue(value, 0, 10 * 3600)
            : getCSSVariable("--accent")
        }
        cx={heatmapPos.xPos}
        cy={heatmapPos.yPos}
        r={heatmapSettings.radius}
      />

      {/* Tooltip group */}
      {value > 0 &&
        <g
          className="
      opacity-0 group-hover:opacity-100 
      transition-opacity duration-150 
      pointer-events-none
    "
        >
          {/* Tooltip background */}
          <text
            x={heatmapPos.xPos - 2 * heatmapSettings.radius} // horizontally centered inside rect
            y={heatmapPos.yPos + heatmapSettings.radius} // vertically centered (adjust as needed)
            className="fill-white  select-none"
            fontSize={4 * heatmapSettings.radius}
            textAnchor="end"
            stroke='black'
            fill='white'
            strokeWidth={1}
            fontWeight={1000}
          >
            {constructDurationString(value)}
          </text>

        </g>
      }
    </g>


  )
}

function HeatmapMonthLabels(
  {
    heatmapSettings
  }: {
    heatmapSettings: HeatmapSettings
  }
) {
  const monthLabels = getMonthNames().map((monthName, monthIndex) => {
    const firstDay = new Date(Date.UTC(2025, monthIndex, 1)) // utc cus otherwise it defaults to local
    const heatmapPos = getHeatmapPosition(8, monthIndex, getWeekNumber(firstDay) + 1.5, heatmapSettings)
    return (
      <text
        key={"label " + monthName}
        x={heatmapPos.xPos - heatmapSettings.radius}
        y={heatmapPos.yPos + 0.5 * heatmapSettings.radius}
        fill='white'
      >
        {monthName.slice(0, 3)}
      </text>
    )
  })
  return monthLabels
}

function DayCircleMatrix(
  {
    heatmapData,
    heatmapSettings,
  }: {
    heatmapData: HeatmapDataType,
    heatmapSettings: HeatmapSettings,
  }
) {

  const circleSvgMatrix = getAllUTCdatesInYear(2025).map(date => {
    return (
      <DayCircleCell
        date={date}
        value={heatmapData[date.toDateString()]}
        heatmapSettings={heatmapSettings}
      />
    )
  })
  return circleSvgMatrix
}


export function HeatmapVisual(
  {
    data,
    heatmapSettings = DEFAULT_HEATMAP_SETTINGS,
  }: {
    data: Record<string, string | number>[],
    heatmapSettings?: HeatmapSettings,
  }
) {
  const [heatmapData, setHeatmapData] = useState<HeatmapDataType>({})
  useEffect(() => {
    const dateValueDict: unknown= _(data)
      .map((row: Record<string, string | number>) => ({
        date: getUTCDateOnly(row.start_time as string).toDateString(), // "YYYY-MM-DD"
        value: row.usage,
      }))
      .groupBy("date")
      .mapValues((rows: Record<string, string | number>[]) => _.sumBy(rows, "value"))
      .value();
    setHeatmapData(dateValueDict as HeatmapDataType)
  }, [data])

  return (
    <svg width={1127} height="100%">
      <DayCircleMatrix heatmapData={heatmapData} heatmapSettings={heatmapSettings} />
      <HeatmapMonthLabels heatmapSettings={heatmapSettings} />
    </svg>
  )
}

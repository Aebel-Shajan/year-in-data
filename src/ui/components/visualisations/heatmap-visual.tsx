
import { useEffect, useState, type MouseEventHandler } from "react";
import { useTooltip, useTooltipInPortal, TooltipWithBounds } from '@visx/tooltip';
import { localPoint } from '@visx/event';

// Types
const DEFAULT_HEATMAP_SETTINGS: HeatmapSettings = {
  radius: 7,
  daySpacing: 2,
  monthSpacing: 20,
  xOffset: 0,
  yOffset: 0,
}

export interface InputHeatmapData {
  date: string,
  value: number,
  label?: string
}
export type HeatmapDataType = {
  [date: string]: {
    value: number,
    label: string
  }
}

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
    handleMouseOver,
    label,
    range,
    heatmapSettings = DEFAULT_HEATMAP_SETTINGS,
  }: {
    date: Date,
    value: number,
    handleMouseOver: CallableFunction
    label: string,
    range: [number, number],
    heatmapSettings?: HeatmapSettings,
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
            ? getColorFromValue(value, range[0], range[1])
            : getCSSVariable("--accent")
        }
        cx={heatmapPos.xPos}
        cy={heatmapPos.yPos}
        r={heatmapSettings.radius}
        onMouseOver={(event) => handleMouseOver(event, value) as MouseEventHandler}
        // onMouseOut={hideTooltip}
      />


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
    range,
    handleMouseOver,
  }: {
    heatmapData: HeatmapDataType,
    heatmapSettings: HeatmapSettings,
    range: [number, number],
    handleMouseOver: CallableFunction
  }
) {



  const circleSvgMatrix = getAllUTCdatesInYear(2025).map(date => {
    const row = heatmapData[date.toDateString()]
    return (
      <DayCircleCell
        date={date}
        value={heatmapData[date.toDateString()].value}
        label={heatmapData[date.toDateString()].label}
        heatmapSettings={heatmapSettings}
        range={range}
        handleMouseOver={handleMouseOver}
      />
    )
  })
  return circleSvgMatrix
}

// beware of this



export function HeatmapVisual(
  {
    data,
    range,
    heatmapSettings = DEFAULT_HEATMAP_SETTINGS,
  }: {
    data: InputHeatmapData[], // always take data in as llist of rows, no maps here
    heatmapSettings?: HeatmapSettings,
    range: [number, number]
  }
) {

  const initialHeatmapData = getAllUTCdatesInYear(2025).reduce((dateMap: HeatmapDataType, date: Date) => {
    dateMap[date.toDateString()] = {
      value: 0,
      label: ""
    }
    return dateMap
  }, {} as HeatmapDataType)


  const [heatmapData, setHeatmapData] = useState<HeatmapDataType>(initialHeatmapData)
  useEffect(() => {
    // convert to map for easier use
    const dateValueDict: HeatmapDataType = data.reduce((heatmapData: HeatmapDataType, row: InputHeatmapData) => {
      const date = (new Date(row.date)).toDateString()
      heatmapData[date] = {
        value: row.value,
        label: row.label ?? ""
      }
      return heatmapData
    }, initialHeatmapData)
    setHeatmapData(dateValueDict as HeatmapDataType)
  }, [data])


  const {
    tooltipData,
    tooltipLeft,
    tooltipTop,
    tooltipOpen,
    showTooltip,
    hideTooltip,
  } = useTooltip();


  // `Tooltip` or `TooltipWithBounds` and remove `containerRef`
  const { containerRef, TooltipInPortal } = useTooltipInPortal({
    // use TooltipWithBounds
    detectBounds: true,
    // when tooltip containers are scrolled, this will correctly update the Tooltip position
    scroll: true,
  })

  const handleMouseOver = (event, datum) => {
    const coords = localPoint(event.target.ownerSVGElement, event);
    if (coords) {
      showTooltip({
        tooltipLeft: coords.x,
        tooltipTop: coords.y,
        tooltipData: datum
      });
    }

  };


  return (
    <>
      <svg ref={containerRef} width={1127} height="100%">
        <DayCircleMatrix heatmapData={heatmapData} heatmapSettings={heatmapSettings} range={range} handleMouseOver={handleMouseOver}/>
        <HeatmapMonthLabels heatmapSettings={heatmapSettings} />
      </svg>
      {tooltipOpen && (
        <TooltipInPortal
          // set this to random so it correctly updates with parent bounds
          key={Math.random()}
          top={tooltipTop}
          left={tooltipLeft}
        >
          Data value <strong>{tooltipData ? String(tooltipData) : "No data"}</strong>
        </TooltipInPortal>
      )}
    </>
  )
}

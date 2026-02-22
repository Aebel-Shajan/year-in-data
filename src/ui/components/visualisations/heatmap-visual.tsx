
import { useEffect, useMemo, useState, type MouseEventHandler } from "react";
import { useTooltip, useTooltipInPortal } from '@visx/tooltip';
import { localPoint } from '@visx/event';
import { useParentSize } from "@visx/responsive";

// Types
const DEFAULT_HEATMAP_SETTINGS: HeatmapSettings = {
  radius: 7,
  daySpacing: 2,
  monthSpacing: 40,
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
    "#D2F3D4",  // soft pale mint highlight
    "#53A36D", // mid pastel green
    "#7FD699", // bright mint green
    "#357A4F", // forest/muted green (low intensity)
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
    label,
    handleMouseOver,
    hideTooltip,
    range,
    heatmapSettings = DEFAULT_HEATMAP_SETTINGS,
  }: {
    date: Date,
    value: number,
    handleMouseOver: CallableFunction,
    hideTooltip: () => void,
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
        onMouseOver={(event) => handleMouseOver(event, { date: date.toDateString(), value, label }) as MouseEventHandler}
        onMouseOut={() => hideTooltip()}
      />
    </g>
  )
}

function HeatmapMonthLabels(
  {
    year,
    heatmapSettings
  }: {
    year: number,
    heatmapSettings: HeatmapSettings
  }
) {
  const monthLabels = getMonthNames().map((monthName, monthIndex) => {
    const firstDay = new Date(Date.UTC(year, monthIndex, 1)) // utc cus otherwise it defaults to local
    const heatmapPos = getHeatmapPosition(8, monthIndex, getWeekNumber(firstDay) + 1.5, heatmapSettings)
    return (
      <text
        fontSize={heatmapSettings.radius * 2}
        key={"label " + monthName}
        x={heatmapPos.xPos - heatmapSettings.radius}
        y={heatmapPos.yPos + 0.5 * heatmapSettings.radius}
        fill={getCSSVariable("--foreground")}
      >
        {monthName.slice(0, 3)}
      </text>
    )
  })
  return monthLabels
}

// beware of this



export function HeatmapVisual(
  {
    year,
    data,
    range,
  }: {
    year: number,
    data: InputHeatmapData[], // always take data in as llist of rows, no maps here
    range: [number, number]
  }
) {



const heatmapData = useMemo(() => {
  const base = getAllUTCdatesInYear(year).reduce(
    (map: HeatmapDataType, date) => {
      map[date.toDateString()] = { value: 0, label: "" }
      return map
    },
    {} as HeatmapDataType
  )

  return data.reduce((map, row) => {
    const date = new Date(row.date).toDateString()
    map[date] = {
      value: row.value,
      label: row.label ?? "",
    }
    return map
  }, base)
}, [year, data])

  const [settings, setSettings] = useState(DEFAULT_HEATMAP_SETTINGS)
  const { parentRef, width } = useParentSize({ debounceTime: 150 });
  const adjustedWidth = Math.max(width, 700)

  useEffect(() => {
    setSettings((old) => {
      const {xOffset, daySpacing} = old
      const newMonthSpacing = (adjustedWidth/12) * 0.3
      const offset = (52 * daySpacing) + (newMonthSpacing*11.5) + xOffset
      const newRadius = (adjustedWidth - offset)/105
      return {
        ...old,
        radius:  newRadius,
        monthSpacing: newMonthSpacing
      }
    })

  }, [adjustedWidth])




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

  const handleMouseOver = (event: MouseEvent, datum: any) => {
    const ownerSVGElement = (event.target as SVGElement).ownerSVGElement;
    if (ownerSVGElement) {
      const coords = localPoint(ownerSVGElement, event);
      if (coords) {
        showTooltip({
          tooltipLeft: coords.x,
          tooltipTop: coords.y,
          tooltipData: datum
        });
      }
    }
  };

  const fullHeight = getHeatmapPosition(9, 0, 0, settings).yPos

  const tooltipDataTyped = tooltipData as { date: string, value: number, label: string }
  return (
    <div className="w-full h-fit overflow-scroll" ref={parentRef}>
      <svg ref={containerRef} width={adjustedWidth} height={fullHeight} >
        {
          // render circles for each daty
          getAllUTCdatesInYear(year).map(date => {
            const row = heatmapData[date.toDateString()]
            return (
              <DayCircleCell
                date={date}
                value={row.value}
                label={row.label}
                heatmapSettings={settings}
                range={range}
                handleMouseOver={handleMouseOver}
                hideTooltip={hideTooltip}
              />
            )
          })
        }
        <HeatmapMonthLabels heatmapSettings={settings} year={year} />
      </svg>
      {
        // tooltip for circles
        tooltipOpen && (
          <TooltipInPortal
            // set this to random so it correctly updates with parent bounds
            key={Math.random()}
            top={tooltipTop}
            left={tooltipLeft}
          >
            {tooltipDataTyped &&
              <>
                <h1>{String(tooltipDataTyped["date"])}</h1>
                <strong>{tooltipData ? String(tooltipDataTyped["label"]) : "No data"}</strong>
              </>
            }
          </TooltipInPortal>
        )
      }
    </div>
  )
}

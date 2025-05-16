import * as d3 from "d3";
import { v4 as uuidv4 } from 'uuid';
import { shadeColor } from "./d3Utils";



type HeatmapData = {
  date: string; // ISO string: "2025-04-11"
  value: number;
  category: string;
};

type Props = {
  data: HeatmapData[];
  units: string;
  year: number;
  colorScale: CallableFunction;
  cellSize?: number;
  cellPadding?: number;
  cellRadius?: number;
  colorRange?: [string, string];
};

export const AnnualHeatmap: React.FC<Props> = ({
  data,
  units,
  year,
  colorScale,
  cellSize = 13,
  cellPadding = 3,
  cellRadius = 2,
}) => {
  const uniqueTooltipId = uuidv4();
  const filteredData = data.filter(row => row.value as number > 0)
  const groupedData = d3.rollup(
    filteredData,
    v => d3.sum(v, d => d.value),
    d => d.date,
    d => d.category,
  )
  const days = d3.timeDays(new Date(year, 0, 1), new Date(year + 1, 0, 1));


  const weeksInYear = d3.timeWeek.count(
    d3.timeYear(new Date(year, 0, 1)),
    new Date(year + 1, 0, 1)
  );

  const margin = {
    left: 35,
    top: 35
  }
  const width = (cellSize + cellPadding) * (weeksInYear + 1) - cellPadding + margin.left ;
  const height = (cellSize + cellPadding) * 7 - cellPadding +  margin.top;


  const allDaysRects = days.map((date) => {
    const week = d3.timeWeek.count(d3.timeYear(date), date);
    const day = date.getDay();
    const dateStr = date.toISOString().slice(0, 10);
    const categoryEntries = Array.from(groupedData.get(dateStr)?.entries() || []).sort((a, b) => (b[1] - a[1]) );
    const totalValue = categoryEntries.reduce(
      (prev: number, current: [string, number]) => {
        return prev + current[1];
      }
    , 0);

    const uniqueRectId = uuidv4();
    const stroke = {
      width: 0.07 * cellSize,
      color: shadeColor(colorScale(totalValue), -10)
    }

    const rectPos = {
      x: week * (cellSize + cellPadding),
      y: day * (cellSize + cellPadding)
    }
    return (
      <>
        {
          week == 1 &&
          <text
            x={-cellPadding}
            y={rectPos.y + 0.5 * cellSize}
            fontSize={(margin.left - cellPadding)/2.5}
            textAnchor="end"
            alignmentBaseline="middle"
          >
            {date.toLocaleDateString(undefined, { weekday: 'long' }).slice(0, 3)}
          </text>
        }
        {
          day === 0 && date.getDate() <= 7 && (
            <text
              x={rectPos.x + 0.5 * cellSize}
              y={-cellPadding}
              fontSize={(margin.left - cellPadding)/2.5}
              textAnchor="middle"
            >
              {date.toLocaleDateString(undefined, { month: 'short' })}
            </text>
          )
        }
        <rect
          key={uniqueRectId}
          x={rectPos.x}
          y={rectPos.y}
          width={cellSize}
          height={cellSize}
          fill={colorScale(totalValue)}
          rx={cellRadius}
          id={uniqueRectId}
          stroke={stroke.color}
          strokeWidth={stroke.width}

          onMouseMove={(e) => {
            // not using state because it causes this element to rerender like a bijiliion times
            const tooltipElement = document.getElementById(uniqueTooltipId);
            if (tooltipElement) {
              tooltipElement.style.display = "block";
              tooltipElement.style.left = `${e.clientX + 20}px`;
              tooltipElement.style.top = `${e.clientY}px`;
              let innerHTML = `
              <p>
                ${dateStr} (${date.toLocaleDateString(undefined, { weekday: 'long' })})
              </p>`
              categoryEntries.slice(0, 3).forEach(entry => {
                innerHTML += `
              <p>
                ${entry[0]} ${Number(entry[1].toPrecision(3))} ${units}
              </p>
                `
              })
              tooltipElement.innerHTML = innerHTML;
            }
            const rectElement = document.getElementById(uniqueRectId)
            if (rectElement) {
              rectElement.style.stroke = "black"
              rectElement.style.strokeWidth = `${stroke.width}`
            }
          }}

          onMouseLeave={() => {
            const tooltipElement = document.getElementById(uniqueTooltipId);
            if (tooltipElement) {
              tooltipElement.style.display = "none";
            }
            const rectElement = document.getElementById(uniqueRectId)
            if (rectElement) {
              rectElement.style.stroke = stroke.color
            }
          }}
        >
        </rect>
      </>
    );
  })

  return (
    <div className="w-full relative overflow-scroll">
      <svg width={width} height={height}>
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          {allDaysRects}
        </g>
      </svg>
      <div
        className="
        fixed bg-white 
        border-blue-100  border-solid 
        rounded-xs p-2 
        pointer-events-none 
        text-xs z-999 
        flex-col gap-0 shadow-2xs hidden"
        id={uniqueTooltipId}
      />
    </div>
  );
};

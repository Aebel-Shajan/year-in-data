import * as d3 from "d3";
import { v4 as uuidv4 } from 'uuid';



type HeatmapData = {
  date: string; // ISO string: "2025-04-11"
  value: number;
};

type Props = {
  data: HeatmapData[];
  units: string;
  year: number;
  domain: [number, number]
  colorScheme?: readonly (readonly string[])[];
  cellSize?: number;
  cellPadding?: number;
  cellRadius?: number;
  colorRange?: [string, string];
};

export const AnnualHeatmap: React.FC<Props> = ({
  data,
  units,
  year,
  domain,
  colorScheme = d3.schemeGreens,
  cellSize = 13,
  cellPadding = 6,
  cellRadius = 2,
}) => {
  const uniqueTooltipId = uuidv4();
  const filteredData = data.filter(row => row.value as number > 0)
  const groupedData = d3.rollup(
    filteredData,
    v => d3.sum(v, d => d.value),
    d => d.date,
  )
  const days = d3.timeDays(new Date(year, 0, 1), new Date(year + 1, 0, 1));

  const ticks = d3.ticks(domain[0], domain[1], 4).filter((value) => value !== 0)
  ticks.unshift(0.001)
  ticks.pop()
  let colorRange = colorScheme[ticks.length + 1] as string[]
  colorRange = ["#EFF2F5", ...colorRange.filter((_, index) => index != 0)]
  const colorScale = d3.scaleThreshold(ticks, colorRange);

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
    const value = groupedData.get(dateStr) || 0;
    const uniqueRectId = uuidv4();
    const stroke = {
      width: 0.07 * cellSize,
      color: shadeColor(colorScale(value), -10)
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
          fill={colorScale(value)}
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
              tooltipElement.innerHTML = `<p>${dateStr} (${date.toLocaleDateString(undefined, { weekday: 'long' })})</p><p>${Number(value.toPrecision(3))} ${units}</p>`;
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
    <div className="w-full relative overflow-scroll"


    >

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
      <div className="sticky left-0">
        <Legend
          colorRange={colorRange}
          ticks={ticks}
        />
      </div>

    </div>

  );
};


type LegendProps = {
  colorRange: string[];
  ticks: number[];
};

const Legend: React.FC<LegendProps> = ({ colorRange, ticks }) => {
  const uniqueTooltipId = uuidv4();
  const legendBoxSize = 20
  const spacing = 10
  const fontSize = 8
  const fullWidth = (legendBoxSize + spacing) * (ticks.length + 1) + spacing
  const fullHeight = legendBoxSize + 2 * spacing + fontSize

  return (
    <>
      <svg
        width={fullWidth}
        height={fullHeight}
      >
        {colorRange.map((color, index) => {
          const x = (index * (legendBoxSize + spacing)) + spacing
          const y = spacing
          const tickValue = index == 0 ? 0 : (index == 1 ? ">0" : ticks[index - 1])
          const uniqueRectId = uuidv4();

          return (
            <g
              key={index}
            >
              <rect
                id={uniqueRectId}
                key={index}
                x={x}
                y={y}
                width={legendBoxSize}
                height={legendBoxSize}
                fill={color}
                rx={4}
                onMouseMove={(e) => {
                  // not using state because it causes this element to rerender like a bijiliion times
                  const tooltipElement = document.getElementById(uniqueTooltipId);
                  if (tooltipElement) {
                    tooltipElement.style.display = "block";
                    tooltipElement.style.left = `${e.clientX + 20}px`;
                    tooltipElement.style.top = `${e.clientY}px`;
                    tooltipElement.innerHTML = `<p>more than ${tickValue}</p>`;
                  }
                  const rectElement = document.getElementById(uniqueRectId)
                  if (rectElement) {
                    rectElement.style.stroke = "black"
                    rectElement.style.strokeWidth = `${0.1 * legendBoxSize}`
                  }
                }}
                onMouseLeave={() => {
                  const tooltipElement = document.getElementById(uniqueTooltipId);
                  if (tooltipElement) {
                    tooltipElement.style.display = "none";
                  }
                  const rectElement = document.getElementById(uniqueRectId)
                  if (rectElement) {
                    rectElement.style.strokeWidth = `${0}`
                  }
                }}
              />
              <text
                x={x}
                y={y + spacing + legendBoxSize + 0.5 * fontSize}
                fontSize={fontSize}
              >
                {tickValue}
              </text>
            </g>
          )
        })}
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
    </>
  );
};


//https://stackoverflow.com/a/13532993
function shadeColor(color: string, percent: number) {

  let R = parseInt(color.substring(1, 3), 16);
  let G = parseInt(color.substring(3, 5), 16);
  let B = parseInt(color.substring(5, 7), 16);

  R = R * (100 + percent) / 100;
  G = G * (100 + percent) / 100;
  B = B * (100 + percent) / 100;

  R = (R < 255) ? R : 255;
  G = (G < 255) ? G : 255;
  B = (B < 255) ? B : 255;

  R = Math.round(R)
  G = Math.round(G)
  B = Math.round(B)

  const RR = ((R.toString(16).length == 1) ? "0" + R.toString(16) : R.toString(16));
  const GG = ((G.toString(16).length == 1) ? "0" + G.toString(16) : G.toString(16));
  const BB = ((B.toString(16).length == 1) ? "0" + B.toString(16) : B.toString(16));

  return "#" + RR + GG + BB;
}
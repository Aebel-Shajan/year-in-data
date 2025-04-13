import { useMemo, useState } from "react";
import * as d3 from "d3";

const BAR_PADDING = 0.3;

type BarplotProps = {
  data: { name: string; value: number }[];
  width: number,
  height: number,
  className?: string,
  barColor?: string;
  sort?: boolean;
};

export const Barplot = (
  {
    data,
    width,
    height,
    className = "",
    sort = true,
    barColor = "#9d174d",
  }:
    BarplotProps
) => {
  const [tooltip, setTooltip] = useState<{
    visible: boolean;
    x: number;
    y: number;
    content: string;
  }>({ visible: false, x: 0, y: 0, content: "" });

  data = d3.rollups(
    data,
    (v) => d3.sum(v, (d) => d.value),
    (d) => d.name
  ).map(([name, value]) => ({ name, value }));
  if (sort) {
    data = data.sort((a, b) => b.value - a.value);
  }
  const groups = data.map((d) => d.name);

  const barWidth = 25;
  const totalHeight = barWidth * groups.length;

  const yScale = useMemo(() => {
    return d3
      .scaleBand()
      .domain(groups)
      .range([0, totalHeight])
      .padding(BAR_PADDING);
  }, [data, height]);

  const xScale = useMemo(() => {
    const [, max] = d3.extent(data.map((d) => d.value));
    return d3
      .scaleLinear()
      .domain([0, max || 10])
      .range([0, 0.9 * width]);
  }, [data, width]);

  const allShapes = data.map((d, i) => {
    const y = yScale(d.name);
    if (y === undefined) {
      return null;
    }

    return (
      <g
        key={i}
        onMouseEnter={(e) =>
          setTooltip({
            visible: true,
            x: e.clientX,
            y: e.clientY,
            content: `${d.name}: ${d.value}`,
          })
        }
        onMouseMove={(e) =>
          setTooltip({
            visible: true,
            x: e.clientX,
            y: e.clientY,
            content: `${d.name}: ${d.value}`,
          })
        }
        onMouseLeave={() =>
          setTooltip({ visible: false, x: 0, y: 0, content: "" })
        }
      >
        <rect
          x={xScale(0)}
          y={yScale(d.name)}
          width={xScale(d.value)}
          height={yScale.bandwidth()}
          stroke={barColor}
          fill={barColor}
          fillOpacity={0.3}
          strokeWidth={1}
          rx={1}
        />
        <text
          x={xScale(d.value) - 7}
          y={y + yScale.bandwidth() / 2}
          textAnchor="end"
          alignmentBaseline="central"
          fontSize={12}
          opacity={xScale(d.value) > 90 ? 0 : 0}
        >
          {d.value}
        </text>
        <text
          x={xScale(0) + 7}
          y={y + yScale.bandwidth() / 2}
          textAnchor="start"
          alignmentBaseline="central"
          fontSize={12}
        >
          {d.name}
        </text>
      </g>
    );
  });

  const grid = xScale
    .ticks(Math.floor(width / 50))
    .slice(0)
    .map((value, i) => (
      <g key={i}>
        <line
          x1={xScale(value)}
          x2={xScale(value)}
          y1={0}
          y2={height}
          stroke="#808080"
          opacity={0.2}
        />
        <text
          x={xScale(value)}
          y={height - 10}
          alignmentBaseline="central"
          fontSize={9}
          stroke="#808080"
          opacity={0.8}
        >
          {value}
        </text>
      </g>
    ));

  return (
    <div className={className}>
      <div className="relative overflow-hidden w-fit h-fit">
        <svg className="sticky top-0" width={width} height={height}>
          <g width={width} height={height}>
            {grid}
          </g>
        </svg>

        <div className="absolute top-0 w-full h-9/10 overflow-y-scroll">

          <svg className=" " width={width} height={totalHeight}>
            <g width={width} height={height}>{allShapes}</g>
          </svg>
        </div>


        {tooltip.visible && (
          <div
            className="fixed bg-white border-blue-100 border-solid rounded-xs p-1 pointer-events-none text-xs z-999"
            style={{
              left: tooltip.x + 20,
              top: tooltip.y,
            }}
          >
            {tooltip.content}
          </div>
        )}
      </div>
    </div>
  );
};

export default Barplot;
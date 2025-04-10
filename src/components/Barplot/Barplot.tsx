// Cool website would reccomend
// https://www.react-graph-gallery.com/
import { useMemo } from "react";
import * as d3 from "d3";

const BAR_PADDING = 0.3;

type BarplotProps = {
  width: number;
  height: number;
  data: { name: string; value: number }[];
  sort?: boolean
};

export const Barplot = (
  {
    width,
    height,
    data,
    sort = true
  }: BarplotProps
) => {
  data = groupData(data)
  if (sort) {
    data = data.sort((a, b) => b.value - a.value)
  }
  const groups = data.map((d) => d.name);

  const barWidth = 20
  const totalHeight = barWidth * groups.length

  // Y axis is for groups since the barplot is horizontal
  const yScale = useMemo(() => {
    return d3
      .scaleBand()
      .domain(groups)
      .range([0, totalHeight])
      .padding(BAR_PADDING);
  }, [data, height]);

  // X axis
  const xScale = useMemo(() => {
    const [, max] = d3.extent(data.map((d) => d.value));
    return d3
      .scaleLinear()
      .domain([0, max || 10])
      .range([0, width]);
  }, [data, width]);

  // Build the shapes
  const allShapes = data.map((d, i) => {
    const y = yScale(d.name);
    if (y === undefined) {
      return null;
    }

    return (
      <g key={i}>
        <rect
          x={xScale(0)}
          y={yScale(d.name)}
          width={xScale(d.value)}
          height={yScale.bandwidth()}
          opacity={0.7}
          stroke="#9d174d"
          fill="#9d174d"
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
          opacity={xScale(d.value) > 90 ? 0 : 0} // hide label if bar is not wide enough
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
    .ticks(6)
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
          textAnchor="middle"
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
    <div className="relative overflow-y-scroll">
        <svg 
          className="sticky top-0"
          width={width} 
          height={height}
        >
          <g
            width={width}
            height={height}
          >
            {grid}
          </g>
        </svg>

        <svg
          className="absolute top-0 "
          width={width} 
          height={totalHeight}
        >
          <g
            width={width}
            height={height}
          >
            {allShapes}
          </g>

        </svg>
    </div>
  );
};


interface ungroupedData {
  name: string | number;
  value: number;
}

function groupData(data: ungroupedData[]) {
  // Sums values together based on the same name
  const grouped = data.reduce<Record<string | number, number>>((acc, curr) => {
    acc[curr.name] = (acc[curr.name] || 0) + curr.value;
    return acc;
  }, {});

  // Convert the grouped object back into an array
  return Object.entries(grouped).map(([name, value]) => ({
    name,
    value,
  }));
}


export default Barplot;
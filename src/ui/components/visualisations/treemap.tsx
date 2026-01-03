import * as d3 from "d3";



export type TreeNode = {
  type: 'node';
  value: number;
  name: string;
  children: Tree[];
};
export type TreeLeaf = {
  type: 'leaf';
  name: string;
  value: number;
};

export type Tree = TreeNode | TreeLeaf;

const colors = [
  "#e0ac2b",
  "#6689c6",
  "#a4c969",
  "#e85252",
  "#9a6fb0",
  "#a53253",
  "#7f7f7f",
];

type TreemapProps = {
  width: number;
  height: number;
  data: Tree;
};


export const Treemap = ({ width, height, data }: TreemapProps) => {
  const hierarchy = d3.hierarchy(data).sum((d) => d.value);

  const treeGenerator = d3.treemap<Tree>().size([width, height]).padding(4);
  const root = treeGenerator(hierarchy);

  const allShapes = root.leaves().map((leaf, index) => {
    const rectWidth = leaf.x1 - leaf.x0
    const rectHeight = leaf.y1 - leaf.y0
    const textWidth = leaf.data.name.length * 12 * 0.55
    const showText = rectWidth > textWidth && rectHeight > 12 * 0.55
    const id = `leaf-${Math.random().toString(36).substr(2, 9)}`;
    return (
      <>
        <g>
          <clipPath id={`clip-${id}`}>
            <rect x={leaf.x0} y={leaf.y0} width={rectWidth} height={rectHeight} />
          </clipPath>
        </g>
        <g key={leaf.id}
        clipPath={`url(#clip-${id})`}
          className="select-none group hover:opacity-100">
          <rect
            x={leaf.x0}
            y={leaf.y0}
            width={rectWidth}
            height={rectHeight}
            stroke="transparent"
            fill={colors[index % colors.length]}
            className={'opacity-80 group-hover:opacity-100'}
          />
          {showText &&
            <>
              <text
                x={leaf.x0 + 3}
                y={leaf.y0 + 3}
                fontSize={12}
                textAnchor="start"
                alignmentBaseline="hanging"
                fill="white"
                className="font-bold"
              >
                {leaf.data.name}
              </text>
              <text
                x={leaf.x0 + 3}
                y={leaf.y0 + 18}
                fontSize={12}
                textAnchor="start"
                alignmentBaseline="hanging"
                fill="white"
                className="font-light"
              >
                {leaf.data.value}
              </text>
            </>
          }
        </g>
      </>
    );
  });

  return (
      <svg width={width} height={height}>
        {allShapes}
      </svg>
  );
};

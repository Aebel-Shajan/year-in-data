import * as d3 from "d3";
import { useParentSize } from '@visx/responsive';
import { useTooltip, useTooltipInPortal } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { useCallback } from "react";



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
  data: Tree;
};

function TreeNodeElement(
  {
    leaf,
    index,
    handleMouseOver,
    hideTooltip
  }: {
    leaf: d3.HierarchyRectangularNode<Tree>,
    index: number,
    handleMouseOver: CallableFunction,
    hideTooltip: CallableFunction
  }
) {

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
        className="select-none group hover:opacity-100"
        onMouseMove={(event) => handleMouseOver(event, { name: leaf.data.name, value: leaf.data.value })}
        onMouseOut={() => hideTooltip()}
      >
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
}


export const Treemap = ({ data }: TreemapProps) => {

  const { parentRef, width, height } = useParentSize({ debounceTime: 150 });
  const {
    tooltipData,
    tooltipLeft,
    tooltipTop,
    tooltipOpen,
    showTooltip,
    hideTooltip,
  } = useTooltip<{ name: string; value: number }>();
  const { containerRef, TooltipInPortal } = useTooltipInPortal({
    // use TooltipWithBounds
    detectBounds: true,
    // when tooltip containers are scrolled, this will correctly update the Tooltip position
    scroll: true,
  })

  // event handlers
  const handlePointerMove = useCallback(
    (event: React.PointerEvent<HTMLDivElement>, datum: any) => {
      // coordinates should be relative to the container in which Tooltip is rendered
      const ownerSVGElement = (event.target as SVGElement).ownerSVGElement;
      if (ownerSVGElement) {

        const containerX = ('clientX' in event ? event.clientX : 0) - ownerSVGElement.getBoundingClientRect().left;
        const containerY = ('clientY' in event ? event.clientY : 0) - ownerSVGElement.getBoundingClientRect().top;
        showTooltip({
          tooltipLeft: containerX,
          tooltipTop: containerY,
          tooltipData: datum
        });
      }
    },
    [showTooltip, tooltipData],
  );

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

  const hierarchy = d3.hierarchy(data).sum((d) => d.value);

  const treeGenerator = d3.treemap<Tree>().size([width, height]).padding(4);
  const root = treeGenerator(hierarchy);


  return (
    <div ref={parentRef} className="h-full w-full">
      <svg width={width} height={height} ref={containerRef}>
        {
          root.leaves().map((leaf, index) => {
            return <TreeNodeElement
              leaf={leaf}
              index={index}
              handleMouseOver={handlePointerMove}
              hideTooltip={hideTooltip}
            />
          })
        }
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
            {tooltipData &&
              <>
                <h1>{String(tooltipData["name"])}</h1>
                <strong>{tooltipData ? String(tooltipData["value"]) : "No data"}</strong>
              </>
            }
          </TooltipInPortal>
        )
      }
    </div>
  );
};

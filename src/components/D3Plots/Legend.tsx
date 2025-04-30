import { v4 as uuidv4 } from 'uuid';

type LegendProps = {
  colorScale: CallableFunction;
  ticks: number[];
};

const Legend: React.FC<LegendProps> = ({ colorScale, ticks }) => {
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
        {ticks.map((tickValue, index) => {
          const x = (index * (legendBoxSize + spacing)) + spacing
          const y = spacing
          const uniqueRectId = uuidv4();
          const color = colorScale(tickValue)

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

export default Legend
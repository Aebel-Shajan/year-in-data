import { useEffect, useState } from "react"
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
import { drawHeatmap } from "./heatmapUtils";
import "./Heatmap.css";
import * as d3 from "d3";


interface DateValueData {
  date: unknown,
  value: unknown
}

const Heatmap = (
  {
    data,
    name,
    units,
    range,
    year,
    colorScheme = "Blues"
  }:
    {
      data: DateValueData[]
      name: string,
      units: string,
      range: [number, number]
      year: number,
      // https://www.w3.org/TR/css-color-3/#colorunits
      colorScheme?: string,
    }
) => {
  const [cal,] = useState<CalHeatmap>(new CalHeatmap())

  
  useEffect(() => {
    cal.destroy()
    
    drawHeatmap(
      {
        cal: cal,
        itemSelector: `#${name}-heatmap`,
        data: data.filter(row => row.value !== 0.0),
        year: year,
        dateCol: "date",
        valueCol: "value",
        units: units,
        colorScheme: colorScheme,
        colorDomain: d3.ticks(range[0], range[1], 3).slice(0, 4).filter(num => num !== 0)
      }
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data])



  return (
    <div className="w-fit overflow-scroll relative">
      <div id={`${name}-heatmap`} />
      <div
        id={`${name}-heatmap-legend`}
        className="pt-5 sticky left-0"
      />
    </div>

  );
}

export default Heatmap;

import {useEffect, useState } from "react"

import { fetchData } from "../api/axiosClient"
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
import { drawHeatmap } from "./heatmapUtils";



interface UnknownObject {
  [key: string]: object
}

interface ActivityMetaData {
  date_col: string,
  filter_cols: string[],
  value_cols: {
    col: string,
    units: string
  }[]
}


const Heatmap = (
  {
    url,
    name,
  }: 
  {
    url: string,
    name: string
  }
) => {
  const [cal,] = useState(new CalHeatmap())

  useEffect(() => {
    async function getData() {
      const response = await fetchData<UnknownObject>(url)
      const metadata = response["metadata"] as ActivityMetaData
      const data = response["data"] as { [x: string]: number; }[]
      drawHeatmap(
        {
          cal: cal,
          itemSelector: `#${name}-heatmap`,
          data: data,
          dateCol: metadata["date_col"],
          valueCol: metadata["value_cols"][0]["col"],
          units: metadata["value_cols"][0]["units"],
        }
      )
    }
    getData()
  }, [url])


  return (
    <div>
      <div 
        id={`${name}-heatmap`}
        className="w-full"
      />
      <div 
        id={`${name}-heatmap-legend`}
        className="pt-5"
      />
    </div>

  );
}






export default Heatmap;
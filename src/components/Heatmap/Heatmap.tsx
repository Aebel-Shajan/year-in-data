import { useEffect, useState } from "react"

import { fetchData } from "../../api/axiosClient"
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
import { drawHeatmap, getQuantile } from "./heatmapUtils";
import "./Heatmap.css";
import { FiRefreshCcw } from "react-icons/fi";


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
    year,
    colorRange = ['#9AF9A8', '#206D38']
  }:
    {
      url: string,
      name: string,
      year: number,
      // https://www.w3.org/TR/css-color-3/#colorunits
      colorDomain?: number[],
      colorRange?: string[],
    }
) => {
  const [cal,] = useState<CalHeatmap>(new CalHeatmap())
  const [data, setData] = useState<{ [x: string]: number; }[]>([])
  const [metadata, setMetadata] = useState<ActivityMetaData | null>(null)
  const [refreshState, setRefershState] = useState(false)

  useEffect(() => {
    async function getData() {
      const response = await fetchData<UnknownObject>(url)
      const newMetadata = response["metadata"] as ActivityMetaData
      const newData = response["data"] as { [x: string]: number; }[]

      setData(newData)
      setMetadata(newMetadata)
    }
    getData()
  }, [url, refreshState])

  useEffect(() => {
    if (!metadata) return
    cal.destroy()
    const valueColInfo = metadata["value_cols"][0]
    let values = data.map(elem => elem[valueColInfo["col"]])
    values = values.filter((value) => value != 0)
    const colorDomain = [getQuantile(values, 10), getQuantile(values, 90)]
    drawHeatmap(
      {
        cal: cal,
        itemSelector: `#${name}-heatmap`,
        data: data,
        year: year,
        dateCol: metadata["date_col"],
        valueCol: valueColInfo["col"],
        units: valueColInfo["units"],
        colorDomain: colorDomain,
        colorRange: colorRange
      }
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, metadata, refreshState])

  function handleRefresh() {
    setRefershState(old => !old)
  }



  return (
    <div>
      <div
        id={`${name}-heatmap`}
        className={"w-full heatmap"}
      />
      <div className="flex w-full items-center justify-between">

        <div
          id={`${name}-heatmap-legend`}
          className="pt-5"
        />

        <button className="btn" onClick={handleRefresh}>
          <FiRefreshCcw />
        </button>
      </div>
    </div>

  );
}






export default Heatmap;
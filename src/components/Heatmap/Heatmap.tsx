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



const Heatmap = (
  {
    url,
    name,
    year,
    colorDomain,
    colorScheme="Blues"
  }:
    {
      url: string,
      name: string,
      year: number,
      // https://www.w3.org/TR/css-color-3/#colorunits
      colorDomain?: number[],
      colorScheme?: string,
    }
) => {
  const [cal,] = useState<CalHeatmap>(new CalHeatmap())
  const [data, setData] = useState<{ [x: string]: number; }[]>([])
  const [metadata, setMetadata] = useState<object | null>(null)
  const [refreshState, setRefershState] = useState(false)

  useEffect(() => {
    async function getData() {
      const response = await fetchData<UnknownObject>(url)
      const newMetadata = response["metadata"] as UnknownObject
      const newData = response["data"] as { [x: string]: number; }[]
      console.log(newData)
      setData(newData)
      setMetadata(newMetadata)
    }
    getData()
  }, [url, refreshState])

  useEffect(() => {
    if (!metadata) return
    cal.destroy()
    let dateCol = "date"
    let valueCol = "value"
    for (const [column, pandasDType] of Object.entries(metadata)) {
      if (pandasDType === "datetime64[ns]") {
        dateCol = column
      }
      if (["int64", "int32", "float64", "float32"].includes(pandasDType)) {
        valueCol = column
      }
    }
    
    let values = data.map(elem => elem[valueCol])
    values = values.filter((value) => value != 0)
    const calculatedDomain = [getQuantile(values, 20), getQuantile(values, 50), getQuantile(values, 80)].map(num => Math.round(num))

    console.log(name, dateCol, valueCol, metadata)
    drawHeatmap(
      {
        cal: cal,
        itemSelector: `#${name}-heatmap`,
        data: data,
        year: year,
        dateCol:dateCol,
        valueCol: valueCol,
        units: "units",
        colorDomain: colorDomain ? colorDomain : calculatedDomain,
        colorScheme: colorScheme
      }
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, metadata, refreshState])

  function handleRefresh() {
    setRefershState(old => !old)
  }



  return (
    <div className="w-full overflow-x-scroll">
      <div
        id={`${name}-heatmap`}
        className={"heatmap"}
      />
      <div className="flex w-full items-center justify-between sticky left-0">

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
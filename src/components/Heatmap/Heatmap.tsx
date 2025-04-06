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

interface Metadata {
  name: string,
  type: string,
  comment: string
}

interface Data {
  [key: string]: string | number 
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
  const [data, setData] = useState<Data[]>([])
  const [metadata, setMetadata] = useState<Metadata[]>([])
  const [refreshState, setRefershState] = useState(false)

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isMounted = true; // to avoid setting state on unmounted component

    const getData = async () => {
      console.log(isLoading)
      if (isLoading) return;
      setIsLoading(true);
      console.log(isLoading)
      try {
        console.log(`Fetching data from ${url}`)
        const response = await fetchData<UnknownObject>(url)
        const newMetadata = response["metadata"] as Metadata[]
        const newData = response["data"] as Data[]
        if (isMounted) {
          setData(newData)
          setMetadata(newMetadata)
        }
      } catch (error) {
        console.error('Error fetching:', error);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    getData();

    return () => {
      isMounted = false;
    };
  }, [url, refreshState]); // empty dependency array = run once on mount


  useEffect(() => {
    if (!metadata) return
    cal.destroy()
    let dateCol = "date"
    let valueCol = "value"
    for (const column_metadata of metadata) {
        if (column_metadata["comment"].includes("date_column")){
          dateCol = column_metadata["name"]
        }
        if (column_metadata["comment"].includes("value_column") && valueCol=="value") {
          valueCol = column_metadata["name"]
        }
    }
    
    let values = data.map(elem => elem[valueCol]) as number[]
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
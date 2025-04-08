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
  comment: string,
  units: string
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
  const [refreshState, setRefershState] = useState(false)
  const [valueCols, setValueCols] = useState<Metadata[]>([])
  // const [categoryCols, setCategoryCols] = useState<Metadata[]>([])
  const [dateCol, setDateCol] = useState<string>("date")
  const [selectedValueCol, setSelectedValueCol] = useState<number>(0)
  // const [selectedCategoryCol, setSelectedCategoryCol] = useState<number>(-1)
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
          setValueCols(newMetadata.filter((column) => column.comment.includes("value_column")))
          // setCategoryCols(newMetadata.filter((column) => column.comment.includes("category_column")))

          for (const column of newMetadata) {
            if (column.comment.includes("date_column") || column.type == "DATE") {
              setDateCol(column.name)
              break
            }
          }

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
    cal.destroy()

    let valueCol = "value"
    let units = "units"
    let groupValues = "sum"
    if (valueCols.length > selectedValueCol && selectedValueCol != -1) {
      valueCol = valueCols[selectedValueCol].name
      const extractedUnits = extractBracketContent(valueCols[selectedValueCol].comment)
      if (extractedUnits) {
        units = extractedUnits
      }
      if (valueCols[selectedValueCol].comment.includes("max")) {
        groupValues = "max"
      }
    }
    
    let values = data.map(elem => elem[valueCol]) as number[]
    values = values.filter((value) => value != 0)
    const calculatedDomain = [getQuantile(values, 20), getQuantile(values, 50), getQuantile(values, 80)].map(num => Math.round(num))

    drawHeatmap(
      {
        cal: cal,
        itemSelector: `#${name}-heatmap`,
        data: data,
        year: year,
        dateCol:dateCol,
        valueCol: valueCol,
        units: units,
        colorDomain: colorDomain ? colorDomain : calculatedDomain,
        colorScheme: colorScheme,
        groupY: groupValues
      }
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, refreshState, selectedValueCol])

  function handleRefresh() {
    setRefershState(old => !old)
  }

  const valueColOptions = valueCols.map((col, index) => {
    return (
      <option value={index} key={col.name}>{col.name.replace(/_/g, " ") } </option>
    )
  })


  return (
    <div className="w-200 overflow-x-scroll">
      <div
        id={`${name}-heatmap`}
        className={"heatmap"}
      />
      <div className="flex w-full items-center justify-between sticky left-0">

        <div
          id={`${name}-heatmap-legend`}
          className="pt-5"
        />

        <div className="flex items-center gap-2">

        <fieldset className="fieldset">
          <select
            value={selectedValueCol}
            onChange={e => setSelectedValueCol(Number(e.target.value))}
            className="select"
          >
            <option disabled={true} value={-1}>Pick a value column</option>
            {valueColOptions}
          </select>
        </fieldset>

        <button className="btn" onClick={handleRefresh}>
          <FiRefreshCcw />
        </button>
        </div>
      </div>
    </div>

  );
}


function extractBracketContent(str: string) {
  const match = str.match(/\[(.*?)\]/);
  if (match && match[1]) {
    return match[1];
  }
  return null;
}



export default Heatmap;
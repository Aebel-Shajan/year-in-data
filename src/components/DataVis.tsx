import { useEffect, useState } from "react"
import { fetchData } from "../api/axiosClient"
import Select from "./Select"
import Barplot from "./D3Plots/Barplot"
import DateBarPlot from "./D3Plots/DateBarPlot"
import { AnnualHeatmap } from "./D3Plots/AnnualHeatmap"
import * as d3 from "d3";


interface Metadata {
  name: string,
  type: string,
  classification: string,
  units: string
}

interface Data {
  [key: string]: string | number
}

const DataVis = (
  {
    name,
    url,
    year,
    index
  }:
    {
      name: string,
      url: string,
      year: number,
      index: number
    }
) => {

  const d3Colors = [d3.schemeGreens, d3.schemeBlues, d3.schemeOranges, d3.schemePurples, d3.schemeReds]
  const d3ColorIndex = index % d3Colors.length
  const [data, setData] = useState<Data[]>([])
  const [valueCols, setValueCols] = useState<Metadata[]>([])
  const [dateCol, setDateCol] = useState<string>("date")
  const [categoryCol, setCategoryCol] = useState<string | null>(null)
  const [selectedValueCol, setSelectedValueCol] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isMounted = true; // to avoid setting state on unmounted component

    const getData = async () => {
      if (isLoading) return;
      setIsLoading(true);
      console.log(isLoading)
      try {
        console.log(`Fetching data from ${url + "/" + year}`)
        const response = await fetchData(url + "/" + year) as { [keys: string]: unknown }
        const newMetadata = response["metadata"] as Metadata[]
        const newData = response["data"] as Data[]
        if (isMounted) {
          setData(newData)
          setValueCols(newMetadata.filter((column) => column.classification == "value_column"))
          let newDateCol = "date"
          const foundDateCols = newMetadata.filter(column => column.classification == "date_column")
          if (foundDateCols.length > 0) {
            newDateCol = foundDateCols[0].name
          }
          let newCategoryCol = null
          const foundCategoryCols = newMetadata.filter(column => column.classification == "category_column")
          if (foundCategoryCols.length > 0) {
            newCategoryCol = foundCategoryCols[0].name
          }
          setDateCol(newDateCol)
          setCategoryCol(newCategoryCol)
        }
      } catch (error) {
        console.error('Error fetching:', error);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }


    getData();

    return () => {
      isMounted = false;
    };
  }, [url, year]); // empty dependency array = run once on mount

  const [range, setRange] = useState<[number, number] | null>(null);

  useEffect(() => {
    const fetchRange = async () => {
      if (valueCols.length > 0) {
        try {
          const response = await fetchData(url + "/range/" + valueCols[selectedValueCol].name);
          setRange(response as [number, number]);
        } catch (error) {
          console.error('Error fetching range:', error);
        }
      }
    };

    fetchRange();
  }, [selectedValueCol, valueCols, url]);

  if (valueCols.length == 0) return

  return <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-250 max-w-full">
    <div className="flex justify-between">
      <h1 className="text-xl font-semibold">
        {name.replace(/_/g, " ")}
      </h1>
    </div>
    <div className="overflow-x-scroll w-full">

      <AnnualHeatmap
        data={structureData(data, dateCol, valueCols[selectedValueCol].name)}
        units={valueCols[selectedValueCol].units}
        domain={range ? range : [1, 10]}
        colorScheme={d3Colors[d3ColorIndex] }
        year={year}
      />
    </div>
    <div className=" w-full flex flex-col p-10 gap-10">
      <Select
        options={valueCols.map(col => col.name)}
        selectedOptionIndex={selectedValueCol}
        setSelectedOptionIndex={setSelectedValueCol}
      />
    </div>

    <div className="w-full flex flex-col items-center gap-1 pb-10 pt-0">
      {categoryCol &&
        <Barplot
          className="w-full max-w-150 h-70 p-3 bg-gray-100 rounded-md border-gray-300 border-2"
          data={data.map(row => {
            return {
              name: row[categoryCol] as string,
              value: row[valueCols[selectedValueCol].name] as number
            }
          })}
        />
      }
        <DateBarPlot
          className="w-full max-w-150 h-90 p-3 bg-gray-100 rounded-md border-gray-300 border-2"
          data={data.map(row => {
            return {
              date: row[dateCol] as string,
              value: row[valueCols[selectedValueCol].name] as number
            }
          })}
        />
        

    </div>
  </div>
}
export default DataVis;


function structureData(
  data: { [key: string]: unknown }[],
  dateCol: string,
  valueCol: string
) {
  return data.map(row => {
    return {
      date: row[dateCol] as string,
      value: row[valueCol] as number
    }
  })
}


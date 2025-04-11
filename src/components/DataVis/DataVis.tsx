import { useEffect, useState } from "react"
import { fetchData } from "../../api/axiosClient"
import Select from "../Select"
import Heatmap from "../Heatmap/Heatmap"

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

  const d3Colors = ["Greens", "Blues", "Oranges", "Purples", "Reds"]
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
          const foundCategoryCols = newMetadata.filter(column => column.classification == "date_column")
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
  }, [ url, year]); // empty dependency array = run once on mount

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

  if (valueCols.length == 0 ) return 

return <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-250 max-w-full">
    <div className="flex justify-between">
      <h1 className="text-xl font-semibold">
        {name.replace(/_/g, " ")}
      </h1>
    </div>
    <div className="p-3 flex justify-center items-center overflow-x-scroll w-full">

      <Heatmap
        name={name}
        data={structureData(data, dateCol, valueCols[selectedValueCol].name)}
        units={valueCols[selectedValueCol].units}
        range={range?  range: [1, 10]}
        colorScheme={d3Colors[d3ColorIndex]}
        year={year}
      />
    </div>
    <div className="flex w-full">
      <Select
        options={valueCols.map(col => col.name)}
        selectedOptionIndex={selectedValueCol}
        setSelectedOptionIndex={setSelectedValueCol}
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
      date: row[dateCol],
      value: row[valueCol]
    }
  })
}


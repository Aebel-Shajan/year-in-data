import { useEffect, useMemo, useState } from "react"
import { fetchData } from "../api/axiosClient"
import Select from "./Select"
import { AnnualHeatmap } from "./D3Plots/AnnualHeatmap"
import * as d3 from "d3";
import {  createColorScale } from "./D3Plots/d3Utils"
import Legend from "./D3Plots/Legend"
import FilterCarousel from "./FilterCarousel/FilterCarousel"

type ColumnCategory = (
  | "date_column" 
  | "value_column" 
  | "time_column" 
  | "category_column" 
  | "image_column" 
  | "link_column"
)
interface ColumnMetdata {
  tag: ColumnCategory | null
  units: string | null
  category: string | null
  range?: [number, number] 
}

interface TableMetadata {
  [column: string]: ColumnMetdata | null
}

interface TableMetadataResponse {
  [schemaName: string]: {
    columns: TableMetadata
  }
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
  const [metadata, setMetadata] = useState<TableMetadata>({})
  const [filteredData, setFilteredData] = useState<Data[]>([])
  const [selectedValueColIndex, setSelectedValueColIndex] = useState<number>(0)
  const [selectedCategoryIndex, setSelectedCategoryIndex] = useState<number>(-1)
  const [isLoading, setIsLoading] = useState(false);
  // const [range, setRange] = useState<[number, number] | null>(null);


  // Date col
  const dateCol: string = getFirstColumnByTag(metadata, "date_column") || "date"

  // Value col
  const possibleValueCols: string[] = getColumnsByTag(metadata, "value_column") 
  const selectedValueCol  = possibleValueCols[selectedValueColIndex] 
  const valueColMetada = metadata[selectedValueCol]
  let valueColUnits = "units"
  if (valueColMetada) {
    if (valueColMetada.units) {
      valueColUnits = valueColMetada.units
    }
  }
  
  // Category col
  const categoryCol: string | null = getFirstColumnByTag(metadata, "category_column")
  const categoryGroups: string[] = useMemo(() => {
    if (!categoryCol) return []
    const uniqueCategories = new Set()
    const newCategoryGroups: string[] = []
    const filteredByYear = data.filter(row => new Date(row[dateCol]).getFullYear() == year)
    filteredByYear.forEach(row => {
      if (!uniqueCategories.has(row[categoryCol])) {
        newCategoryGroups.push(row[categoryCol] as string)
        uniqueCategories.add(row[categoryCol])
      }
    })
    return newCategoryGroups
  }, [categoryCol, data, year])

  // Image col
  const imageCol: string | null = getFirstColumnByTag(metadata, "image_column")
  const imageGroups: { name: string, imageUrl: string }[] = useMemo(() => {
    if (!categoryCol || !imageCol) return []
    const uniqueImages = new Set()
    const newImageGroups: { name: string, imageUrl: string }[] = []
    const filteredByYear = data.filter(row => new Date(row[dateCol]).getFullYear() == year)
    filteredByYear.forEach(row => {
      if (!uniqueImages.has(row[categoryCol])) {
        newImageGroups.push({
          name: row[categoryCol] as string,
          imageUrl: row[imageCol] as string
        })
        uniqueImages.add(row[categoryCol])
      }
    })
    return newImageGroups
  }, [categoryCol, data, imageCol, year])

  // Color scale
  let ticks: number[] = [1, 5, 10]
  if (metadata[selectedValueCol]) {
    const range = metadata[selectedValueCol]["range"]
    if (range) {
      ticks = d3.ticks(range[0], range[1], 4).filter((value) => value !== 0)
      ticks.unshift(0.001)
      ticks.pop()
    }
  }
  const colorScale = createColorScale(ticks, d3Colors[d3ColorIndex])


  



  useEffect(() => {
    const filteredByYear = data.filter(row => new Date(row[dateCol]).getFullYear() == year)
    if (!categoryCol) {
      setFilteredData(filteredByYear)
      return
    }
    if (selectedCategoryIndex == -1 || selectedCategoryIndex >= categoryGroups.length) {
      setFilteredData(filteredByYear)
      return
    }
    if (imageCol) {
      setFilteredData(filteredByYear.filter(
        row => row[categoryCol] == imageGroups[selectedCategoryIndex].name
      ))
    } else {
      setFilteredData(filteredByYear.filter(
        row => row[categoryCol] == categoryGroups[selectedCategoryIndex]
      ))
    }
  }, [selectedCategoryIndex, year])

  useEffect(() => {
    let isMounted = true; // to avoid setting state on unmounted component

    const getData = async () => {
      if (isLoading) return;
      setIsLoading(true);
      console.log(isLoading)
      try {
        console.log(`Fetching data from ${url}`)
        // Fetch csv data, convert to json
        const dataResponse = await fetchData(url) as string
        const data: Data[] = d3.csvParse(dataResponse)
        setData(data)
        const filteredByYear = data.filter(row => new Date(row[dateCol]).getFullYear() == year)
        setFilteredData(filteredByYear)
        // Fetch json metadata
        const metadataResponse = await fetchData("/metadata/" + name + "_metadata.json") as TableMetadataResponse
        const firstKey = Object.keys(metadataResponse)[0];
        const metadata = metadataResponse[firstKey].columns;
        setMetadata(metadata)
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
  }, [url]); // empty dependency array = run once on mount



  return (
    <div className="
      p-2 bg-base-100 border-base-300 border-2 text-base-content rounded-lg w-full 
      max-w-200 flex flex-col gap-3
      "
    >
        <h1 className="font-semibold px-3 py-1 w-fit bg-base-100 ">
          {name.replace(/_/g, " ")}
        </h1>
      <div className=" w-full flex flex-col gap-2">
        <div className="flex  w-full overflow-x-scroll justify-center">

        <AnnualHeatmap
          data={
            structureData(
              filteredData, 
              dateCol, 
              possibleValueCols[selectedValueColIndex], 
              categoryCol,
            )
          }
          units={valueColUnits}
          colorScale={colorScale}
          year={year}
          />
          </div>
          <div className="pl-3">
          <Legend
          ticks={ticks}
          colorScale={colorScale}
          />
          </div>
      </div>
      <div className="flex w-full gap-2">

        {possibleValueCols.length > 1 && (
          <Select
            options={possibleValueCols}
            selectedOptionIndex={selectedValueColIndex}
            setSelectedOptionIndex={setSelectedValueColIndex}
          />
        )}
        {categoryGroups.length > 0 && imageCol == null && (
              <Select
                options={categoryGroups}
                selectedOptionIndex={selectedCategoryIndex}
                setSelectedOptionIndex={setSelectedCategoryIndex}
                defaultValue={"All"}
              />
            )

        }
      </div>
      {imageGroups.length > 0 && 
      (
        <FilterCarousel
          items={imageGroups}
          selectedIndex={selectedCategoryIndex}
          setSelectedIndex={setSelectedCategoryIndex}
        />
      ) 
      }

      {/* <div className="w-full flex flex-col  gap-3  pb-10 pt-0">
        {categoryCol &&
          <Barplot
            className="p-3  rounded border-gray-300 border w-fit"
            width={300}
            height={200}
            barColor={colorScale(ticks[1])}
            data={filteredData.map(row => {
              return {
                name: row[categoryCol] as string,
                value: row[valueCols[selectedValueCol].name] as number
              }
            })}
          />
        }
        <Barplot
          className="p-3 rounded border-gray-300 border w-fit"
          width={300}
          height={200}
          barColor={colorScale(ticks[1])}
          sort={false}
          data={groupByWeekDay(filteredData.map(row => {
            return {
              date: row[dateCol] as string,
              value: row[valueCols[selectedValueCol].name] as number
            }
          }))}
        />
        <Barplot
          className="p-3  rounded border-gray-300 border w-fit"
          width={500}
          height={340}
          barColor={colorScale(ticks[1])}
          sort={false}
          data={groupByMonth(filteredData.map(row => {
            return {
              date: row[dateCol] as string,
              value: row[valueCols[selectedValueCol].name] as number
            }
          }))}
        />


      </div> */}
    </div>
  )
}

export default DataVis;


function structureData(
  data: { [key: string]: unknown }[],
  dateCol: string,
  valueCol: string,
  categoryCol: string | null
) {
  return data.map(row => {
    return {
      date: row[dateCol] as string,
      value: row[valueCol] as number,
      category: categoryCol ? row[categoryCol] as string : ""
    }
  })
}

function getColumnsByTag(
  metadata: TableMetadata, 
  column_category: ColumnCategory,
): string[] {
  
  if (Object.keys(metadata).length == 0) return []
  const value_cols = Object.keys(metadata).filter((key) => {
    if (!metadata[key]) return false
    return metadata[key].tag === column_category
  })
  return value_cols
}

function getFirstColumnByTag(
  metadata: TableMetadata,
  column_category: ColumnCategory,
): null | string  {
  const matchingCols = getColumnsByTag(metadata, column_category)
  if (matchingCols.length > 0) {
    return matchingCols[0]
  }
  return null
}
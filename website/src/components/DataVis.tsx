import { useEffect, useState } from "react"
import { fetchData } from "../api/axiosClient"
import Select from "./Select"
import { AnnualHeatmap } from "./D3Plots/AnnualHeatmap"
import * as d3 from "d3";
import { createColorScale } from "./D3Plots/d3Utils"
import Legend from "./D3Plots/Legend"
// import FilterCarousel from "./FilterCarousel/FilterCarousel"

// type ColumnCategory = (
//   | "date_column" 
//   | "value_column" 
//   | "time_column" 
//   | "category_column" 
//   | "image_column" 
//   | "link_column"
// )

interface ValueColumn {
  name: string;
  units: string;
  range: [number, number];
}

interface CategoryColumn {
  name: string;
  // orderedDistinctCategories?: string[];
  imageColumn?: string;
  // linkColumn?: string;
}

interface TableSchema {
  datetime_column: string;
  value_columns: { [key: string]: ValueColumn };
  category_columns: { [key: string]: CategoryColumn };
}

interface TableEventRecords {
  schema: TableSchema;
  records: Data[]
}

interface Data {
  [key: string]: string | number
}

const DataVisContainer = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="
      p-2 bg-base-100 border-base-300 border-2 text-base-content rounded-lg w-full 
      max-w-200 flex flex-col gap-3
      "
    >
      {children}
    </div>
  )
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
  const d3Colors = [d3.schemeGreens, d3.schemeBlues, d3.schemeOranges, d3.schemePurples]
  const d3ColorIndex = index % d3Colors.length
  const [data, setData] = useState<Data[]>([])
  const [schema, setSchema] = useState<TableSchema | null>(null)
  const [selectedValueCol, setSelectedValueCol] = useState<string | null>(null)
  const [selectedCategoryCol, setSelectedCategoryCol] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    fetchData<TableEventRecords>(url + "/" + year)
      .then(response => {
        setData(response.records)
        const schema = response.schema
        const valueCols = Object.keys(response.schema.value_columns)
        const categoryCols = Object.keys(response.schema.category_columns)
        if (schema.datetime_column.length === 0) {
          setSuccess(false)
          throw new Error("Expected datetime column in schema")
        }
        if (valueCols.length === 0) {
          setSuccess(false)
          throw new Error("No value columns found in schema")
        }
        setSuccess(true)
        if (!selectedValueCol) {
          setSelectedValueCol(valueCols[0])
        }
        if (!selectedCategoryCol) {
          setSelectedCategoryCol(categoryCols[0])
        }
        setSchema(schema)
      })
      .catch(error => {
        console.error('Error fetching:', error);
      })
  }, [url, year]); // empty dependency array = run once on mount

  if (!success || !schema || !selectedValueCol) {
    return <DataVisContainer>
      Error fetching data from {url}
    </DataVisContainer>
  }

  // Date col
  const dateCol: string = schema.datetime_column

  // Category col
  const allCategoryCols: string[] = Object.keys(schema.category_columns)
  const categoryColOptions = allCategoryCols.map(value => {
    return {
      label: value.replace(/_/g, " "),
      value: value
    }
  })

  // Value col
  const possibleValueCols: string[] = Object.keys(schema.value_columns)
  const valueColUnits = schema.value_columns[selectedValueCol].units
  const valueColsOptions = possibleValueCols.map(value => {
    return {
      label: value.replace(/_/g, " "),
      value: value
    }
  })

  // Color scale
  let ticks: number[] = [1, 5, 10]
  const valueColrange = schema.value_columns[selectedValueCol].range
  if (valueColrange) {
    ticks = d3.ticks(valueColrange[0], valueColrange[1], 4).filter((value) => value !== 0)
    ticks.unshift(0.001)
    ticks.pop()
  }
  const colorScale = createColorScale(ticks, d3Colors[d3ColorIndex])


  const heatmap_data = structureData(
    data,
    dateCol,
    selectedValueCol,
    selectedCategoryCol,
  )

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
            data={heatmap_data}
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
        {
          valueColsOptions.length > 1 &&
          <Select
            options={valueColsOptions}
            selectedValue={selectedValueCol}
            setSelectedValue={setSelectedValueCol}
            labelLeft="value column"
          />
        }


        {
          categoryColOptions.length > 0 &&
          <Select
            options={categoryColOptions}
            selectedValue={selectedCategoryCol}
            setSelectedValue={setSelectedCategoryCol}
            labelLeft="category column"
          />
        }
      </div>
      {/* {imageGroups.length > 0 && 
      (
        <FilterCarousel
          items={imageGroups}
          selectedIndex={selectedCategoryIndex}
          setSelectedIndex={setSelectedCategoryIndex}
        />
      ) 
      }  */}

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


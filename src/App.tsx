import { useEffect, useState } from "react";
import Heatmap from "./components/Heatmap/Heatmap";
import Navbar from "./components/Navbar";
import { axiosInstance } from "./api/axiosClient";

const HeatmapInstance = (
  {
    name,
    url,
    year
  }:
  {
    name: string,
    url: string,
    year: number
  }
) => {

  return <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-fit max-w-full">
    <div className="flex justify-between">
      <h1 className="text-xl font-semibold">
        {name.replace("get_", "")}
      </h1>
    </div>
    <div className="p-3 flex justify-center overflow-x-scroll">
      <Heatmap
        url={url + "/" + year}
        name={name}
        year={year}
      />
    </div>
  </div>
}

interface Routes {
  name: string,
  path: string
}

const HomePage = () => {
  const [dataEndpoints, setDataEndpoints] = useState<Routes[]>([])
  const [year, setYear] = useState(2023)


  useEffect(() => {
    axiosInstance
      .get("/retrieve-data/data-routes")
      .then(response => response.data)
      .then((data) => {
        console.log(data)
        const endpoints: Routes[] = []
        const dataRoutes: string[] = data.data
        dataRoutes.forEach(route => {
          endpoints.push({
            "name": route,
            "path": "/retrieve-data/" + route
          })
        })
        setDataEndpoints(endpoints)
      })
      .catch(e => console.error(e))

  }, [])

  const heatmaps = dataEndpoints.map((route, index) => {
    return (<HeatmapInstance
      key={index + "_heatmap"}
      name={route.name}
      url={route.path}
      year={year}
    />)
  })

  return (
    <div className="min-h-screen bg-base-200 max-w-screen overflow-x-hidden">
      <Navbar
        year={year}
        setYear={setYear}    
      />

      <div className="p-8 min-h-screen w-full flex flex-col items-center gap-5 pt-20">
        {heatmaps}
      </div>

    </div>
  );
};

export default HomePage;

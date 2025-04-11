import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import { axiosInstance } from "./api/axiosClient";
import DataVis from "./components/DataVis/DataVis";



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
    return (<DataVis
      key={index + "_heatmap"}
      name={route.name}
      url={route.path}
      year={year}
      index={index}
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

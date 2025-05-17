import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import DataVis from "./components/DataVis";



interface Routes {
  name: string,
  path: string
}

const HomePage = () => {
  const [dataEndpoints, setDataEndpoints] = useState<Routes[]>([])
  const [year, setYear] = useState(2024)


  useEffect(() => {

        const endpoints: Routes[] = []
        const dataRoutes: string[] = [
          "app_usage_screen_time",
          "kindle_reading",
          "github_repo_contributions",
          "strong_workouts",
          "fitbit_sleep",
          "fitbit_exercise",
          "fitbit_calories",
          "fitbit_steps",

        ]
        dataRoutes.forEach(route => {
          endpoints.push({
            "name": route,
            "path": "/data/" + route + ".csv"
          })
        })
        setDataEndpoints(endpoints)

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

      <div className="min-h-screen w-full flex flex-col items-center gap-5 pt-20">
        {heatmaps}
      </div>

    </div>
  );
};

export default HomePage;

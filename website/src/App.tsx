import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import DataVis from "./components/DataVis";
import { fetchData } from "./api/axiosClient";



interface Routes {
  name: string,
  path: string
}

const HomePage = () => {
  const [dataEndpoints, setDataEndpoints] = useState<Routes[]>([])
  const [year, setYear] = useState(2024)


  useEffect(() => {
    function createEndpoints(tableNames: string[]) {
      const endpoints: Routes[] = []
      tableNames.forEach(tableName => {
        endpoints.push({
          "name": tableName,
          "path": "/tables/" + tableName
        })
      })
      setDataEndpoints(endpoints)
    }

    const orderedTableNames = [
      "app_usage_screen_time",
      "github_repo_contributions",
      "kindle_reading",
      "strong_workouts",
      "fitbit_calories",
      "fitbit_exercise",
      "fitbit_sleep",
      "fitbit_steps",
      "youtube_watch_history",
    ]
    createEndpoints(orderedTableNames)
    // fetchData<string[]>("/tables/list_all_tables")
    //   .then(createEndpoints)
    //   .catch(reason => alert("Unable to get data from backend: " + reason))
  }, [year])


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

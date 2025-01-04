import { useEffect, useState } from "react"
import styles from "./GithubHeatmap.module.css"
import { drawGithubHeatmap, } from "../heatmapUtils"
import { fetchData } from "../../../api/axiosClient"
import { DistinctRepos, GithubData } from "../../../types/dataTypes"
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
import FilterCarousel from "../../../components/FilterCarousel/FilterCarousel"

const GithubHeatmap = () => {
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)
  const [distinctRepos, setDistinctRepos] = useState<DistinctRepos[]>([])
  const [activity, setActivity] = useState<GithubData[]>()
  const [cal,] = useState(new CalHeatmap())

  useEffect(() => {
    async function getData() {
      const data = await fetchData<GithubData[]>("/github-data")
      const distinctRepos = await fetchData<DistinctRepos[]>("/distinct-github-repos")
      setActivity(data)
      drawGithubHeatmap(cal, data)
      setDistinctRepos(distinctRepos)
    }
    getData()
  }, [])

  useEffect(() => {
    if (activity) {
      let newActivity = activity
      if (selectedIndex !== -1) {
        newActivity = activity.filter((data) => {
          return data["repository_name"] === distinctRepos[selectedIndex]["repository_name"]
        })
      }
      drawGithubHeatmap(cal, newActivity)
    }
  }, [selectedIndex])

  return (
    <div
      className={styles.dataSection}
    >
      <h2>Github Activity (From Gitlab)</h2>
      <div
        id="github-heatmap"
        className={styles.heatmap}
      ></div>
      <div id="github-legend"></div>
      <FilterCarousel
        items={distinctRepos.map((repo) => {
          return {
            "name": repo["repository_name"],
            "imageUrl": repo["repository_image"]
          }
        })}
        selectedIndex={selectedIndex}
        setSelectedIndex={setSelectedIndex}
      />
      <p>
        At the start of 2024, I was stressed out because I graduated in 2023 and had
        not been able to land a job despite applying to hundreds of companies. So this
        year I decided to lock in and learn how to code properly.
      </p>
      <p>
        January I made a couple chrome extensions to learn how to use javascript.
        February, March, April I  enrolled in a bootcamp where I learned react, java
        spring boot and working with rest apis. End of april I got my first job as a
        data engineer 🎉. This was when I started learning about data pipelines and doing
        more python related stuff.
      </p>
      <p>
        Ever since then I've just been messing around with projects/tech which I think
        are fun.
      </p>
    </div>
  );
}

export default GithubHeatmap;

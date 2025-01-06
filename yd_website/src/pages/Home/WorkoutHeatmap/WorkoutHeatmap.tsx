import { useContext, useEffect, useState } from "react"
import styles from "./WorkoutHeatmap.module.css"
import { drawWorkoutHeatmap } from "../heatmapUtils"
import { fetchData } from "../../../api/axiosClient"
import { WorkoutData } from "../../../types/dataTypes"
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
import FilterCarousel from "../../../components/FilterCarousel/FilterCarousel"
import { HeatmapContext } from "../HeatmapContext/HeatmapContext"

interface DistinctWorkouts {
  workout_name: string,
  latest_date: string
}

const WorkoutHeatmap = () => {
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)
  const [selectedSubIndex, setSelectedSubIndex] = useState<number>(-1)
  const [distinctWorkouts, setDistinctWorkouts] = useState<DistinctWorkouts[]>([])
  const [distinctExercises, setDistinctExercises] = useState<string[]>([])
  const [activity, setActivity] = useState<WorkoutData[]>([])
  const [workoutCal,] = useState(new CalHeatmap())
  const {showDetails} = useContext(HeatmapContext)

  useEffect(() => {
    async function getData() {
      const data = await fetchData<WorkoutData[]>("/workout-data")
      const distinctWorkouts = await fetchData<DistinctWorkouts[]>("/distinct-workouts")
      setActivity(data)
      drawWorkoutHeatmap(workoutCal, data)
      setDistinctWorkouts(distinctWorkouts)
      setDistinctExercises(getDistinctExercises(data))
    }
    getData()
  }, [workoutCal])

  // If workout changes then reset exercise filter
  useEffect(() => {
    setSelectedSubIndex(-1)
  }, [selectedIndex])

  useEffect(() => {

    let newActivity = activity
    if (selectedIndex !== -1) {
      newActivity = activity.filter((data) => {
        return data["workout_name"] === distinctWorkouts[selectedIndex]["workout_name"]
      })
    }
    setDistinctExercises(getDistinctExercises(newActivity))
    if (selectedSubIndex !== -1) {
      newActivity = newActivity.filter((data) => {
        return data["exercise_name"] === distinctExercises[selectedSubIndex]
      })
    }

    drawWorkoutHeatmap(workoutCal, newActivity)
  }, [selectedIndex, selectedSubIndex])

  return (
    <div
      className={styles.dataSection}
    >
      <h2>Workout Activity (From Strong workout app)</h2>
      <div
        id="workout-heatmap"
        className={styles.heatmap}
      ></div>
      <div id="workout-legend"></div>
      {showDetails &&
        <>
          <FilterCarousel
            items={distinctWorkouts.map((data) => {
              return {
                "name": data["workout_name"]
              }
            })}
            selectedIndex={selectedIndex}
            setSelectedIndex={setSelectedIndex}
          />
          <FilterCarousel
            items={distinctExercises.map((exercise) => {
              return {
                "name": exercise
              }
            })}
            selectedIndex={selectedSubIndex}
            setSelectedIndex={setSelectedSubIndex}
          />


          <p>
            January, February March I was in the gym almost everyday. End of April I started
            working and the frequency has been slowly declining ever since. I think I was
            over doing it at the start going in 5 to 6 times per week. Although, it did help me
            establish the habit of going and this helped me endure the habit till the end of the year.
            I'll probably stick to just 3 to 4 days a week because I'm still
            making roughly the same amount of progress.
          </p>
        </>
      }
    </div>
  );
}

export default WorkoutHeatmap;

/**
 * Loops through workout data to get distinct exercises
 * 
 * @param data Workout data
 * @returns List of distinct exercises
 */
function getDistinctExercises(data: WorkoutData[]): string[] {
  const exerciseMap: { [key: string]: number } = {}
  data.forEach((data) => {
    exerciseMap[data["exercise_name"]] = 0
  })
  return Object.keys(exerciseMap)
}
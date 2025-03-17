import styles from "./Home.module.css"
import ReadingHeatmap from "./ReadingHeatmap/ReadingHeatmap";
import GithubHeatmap from "./GithubHeatmap/GithubHeatmap";
import WorkoutHeatmap from "./WorkoutHeatmap/WorkoutHeatmap";
import TimeSeriesHeatmap from "../../components/TimeSeriesHeatmap/TimeSeriesHeatmap";
import Footer from "../../components/Footer/Footer";
import { DetailsToggleButton, HeatmapProvider } from "./HeatmapContext/HeatmapContext";
import { axiosInstance, postData } from "../../api/axiosClient";

const Home = () => {

  async function updateGithubActivity() {
    const result = await postData("/github/2024")
    alert(result)
  }

  return (
    <div
      className={styles.home}
    >


      <div
        className={styles.mainContent}
      >
        <h1>Year in Data</h1>
        <p>
          2024 is over, 2025 is here. Here is what I was doing this year represented through
          yearly heatmaps.
        </p>

        <a href={axiosInstance.getUri() + "github/auth"} target="_blank">dev login</a>
        <button onClick={updateGithubActivity}>Update github activity</button>

        <HeatmapProvider>
          <DetailsToggleButton />

          <ReadingHeatmap />

          <GithubHeatmap />

          <WorkoutHeatmap />

          <TimeSeriesHeatmap
            name="running"
            filterMap={{
              1: "1 km",
              2: "2 km",
              3: "3 km",
              5: "5 km"
            }}
            units="kilometers"
            dataUrl="/running-data"
            dateCol="date"
            valueCol="distance"
            title="Running (From Fitbit)"
            description="April I decided to get back into running, did it for a few weeks
          then gave up. I started again in June and I was fairly consistent till 
          start of November when the weather got bad.
          "
            colorScheme="Greens"
          />

          <TimeSeriesHeatmap
            name="step"
            filterMap={{
              1000: "low",
              5000: "mid",
              10000: "high"
            }}
            units="steps"
            dataUrl="/steps-data"
            title="Steps per day (From Fitbit)"
            description="I walk 🚶‍♂️"
            colorScheme="PuBuGn"
          />


          <TimeSeriesHeatmap
            name="sleep"
            filterMap={{
              4: "sleep deprived",
              6: "not good not great",
              8: "good sleep",
              10: "overslept"
            }}
            units="hours"
            dataUrl="/sleep-data"
            valueCol="total_duration_hours"
            title="Hours slept per day (From Fitbit)"
            description="Sleep is surprisingly better than expected. I have a feeling this
          is because I extract the time spent in bed rather than actual sleep. I should
          probably fix this at some point. You can see 
          when I lost my Fitbit in February lol."
            colorScheme="Purples"
          />

          <TimeSeriesHeatmap
            name="calorie"
            filterMap={{
              1500: "low",
              2000: "normal",
              3000: "active",
              3500: "very active"
            }}
            units="calories"
            dataUrl="/calorie-data"
            title="Calories burned (From Fitbit)"
            description="Shows how many calories. The average person burns 2500 per day but I'm
          getting days where I burn over 3000. I did some research online and found that
          Fitbit overestimates how many calories a person burns per day by 30%,
          so I have no idea how accurate this is."
            colorScheme="YlOrRd"
          />
        </HeatmapProvider>
      </div>
      <div
        className={styles.footer}
      >
        <Footer />
      </div>
    </div>
  );
}

export default Home;
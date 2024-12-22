import { useEffect, useState } from "react"
import styles from "./ReadingHeatmap.module.css"
import { drawKindleHeatmap } from "../heatmapUtils"
import { fetchData } from "../../../api/axiosClient"
import { DistinctBooks, ReadingData } from "../../../types/dataTypes"
// @ts-expect-error cal-heatmap library don't have declration files :(
import CalHeatmap from 'cal-heatmap';
import FilterCarousel from "../../../components/FilterCarousel/FilterCarousel"

const ReadingHeatmap = () => {
  const [selectedBook, setSelectedBook] = useState<number>(-1)
  const [books, setBooks] = useState<DistinctBooks[]>([])
  const [readingActivity, setReadingActivity] = useState<ReadingData[]>()
  const [readingCal,] = useState(new CalHeatmap())

  useEffect(() => {
    async function getData() {
      const readingData = await fetchData<ReadingData[]>("/kindle-data?year=2024")
      const distinctBooks = await fetchData<DistinctBooks[]>("distinct-kindle-books?year=2024")
      setReadingActivity(readingData)
      drawKindleHeatmap(readingCal, readingData)
      setBooks(distinctBooks)
    }
    getData()
  }, [])

  useEffect(() => {
    if (readingActivity) {
      let newActivity = readingActivity
      if (selectedBook !== -1) {
        newActivity = readingActivity.filter((data) => {
          return data["ASIN"] === books[selectedBook]["ASIN"]
        })
      }
      drawKindleHeatmap(readingCal, newActivity)
    }
  }, [selectedBook])

  return (
    <div
      className={styles.dataSection}
    >
      <h2>Reading Activity (From Amazon Kindle)</h2>
      <div id="reading-heatmap" style={{ height: "7rem" }}></div>
      <div id="reading-legend"></div>

      <FilterCarousel
        items={books.map(book => {
          return {
            name: book.ASIN,
            imageUrl: book.book_image
          }
        })}
        selectedIndex={selectedBook}
        setSelectedIndex={setSelectedBook}
      />
      <p>
        I feel my reading habit comes and goes in waves. Although from september onward
        I've been locked in. That's when I started daily driving the Hisense A9 as my
        phone. It has an e-ink screen so it meant I didn't have to go find my kindle
        to read.
      </p>
    </div>
  );
}

export default ReadingHeatmap;
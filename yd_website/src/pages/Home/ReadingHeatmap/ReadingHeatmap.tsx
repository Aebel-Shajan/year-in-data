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
      const readingData = await fetchData<ReadingData[]>("/kindle-data")
      const distinctBooks = await fetchData<DistinctBooks[]>("/distinct-kindle-books")
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
      <div 
        id="reading-heatmap" 
        className={styles.heatmap}
      ></div>
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
        My goal for this year was to read 20 books, but I only managed to read about 14. I started
        out strong in January and February, but my reading dropped off in March and April. I picked
        the habit back up in May, but the books I was reading couldn't hold my attention. 
        During June, July, and August, I forgot about reading altogether. 
        In September, I replaced my Samsung S10 with an e-ink reader (Hisense A9), 
        and since then, I've been reading almost every single day :].
      </p>
    </div>
  );
}

export default ReadingHeatmap;
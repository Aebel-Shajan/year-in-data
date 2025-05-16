import styles from "./FilterItem.module.css"
import { ItemType } from "../FilterCarousel"
import { useEffect, useState } from "react"


const FilterItem = (
  {
    index,
    selectedIndex,
    setSelectedIndex,
    item,
  }: {
    index: number,
    selectedIndex: number,
    setSelectedIndex: CallableFunction,
    item: ItemType
  }
) => {
  const [loadImage, setLoadImage] = useState(true)
  const classes = [styles.itemContainer]
  if (selectedIndex === index) {
    classes.push(styles.itemSelected)
  }

  useEffect(() => {
    if (!item["imageUrl"] || item["imageUrl"] ==="") {
      setLoadImage(false)
    }
  }, [item])

  let item_url: string | null = item["imageUrl"] as string
  if (item_url === "") {
    item_url = null
  }

  return (
    <div
      className={classes.join(" ")}
      key={`book-${index}`}
      onClick={() => setSelectedIndex(index)}
    >
      {
        loadImage && item_url
          ?
          <img
            className={styles.itemImage}
            src={item_url}
            onError={() => {
              setLoadImage(false)
            }}
          />
          :
          <div
            className={styles.itemText}
          >
            {item["name"]}
          </div>
      }
    </div>
  )
}

export default FilterItem;
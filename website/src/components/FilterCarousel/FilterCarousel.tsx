import { useRef, useState } from "react";
import styles from "./FilterCarousel.module.css"
import itemStyles from "./FilterItem/FilterItem.module.css"
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import FilterItem from "./FilterItem/FilterItem";

export interface ItemType {
  name: string,
  imageUrl?: string,
}

const FilterCarousel = (
  {
    items,
    selectedIndex,
    setSelectedIndex,
    height = 8
  }: {
    items: ItemType[],
    selectedIndex: number,
    setSelectedIndex: CallableFunction,
    height?: number
  }
) => {
  const itemCarousel = useRef<HTMLDivElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  const itemImageElements = items.map((item, index) => {
    return (
      <FilterItem
        index={index}
        selectedIndex={selectedIndex}
        setSelectedIndex={setSelectedIndex}
        item={item}
      />
    )
  })

  const showAllElement = (
    <div
      className={[itemStyles.itemContainer, selectedIndex === -1 ? itemStyles.itemSelected : ""].join(" ")}
      key={`book--1`}
      onClick={() => setSelectedIndex(-1)}
    >
      <div className={itemStyles.itemText}>
        Show all
      </div>
    </div>
  )

  return (
    <div
      className={styles.container}
      style={{ height: `${height}rem` }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div
        className={styles.itemCarouselContainer}
      >
        {itemCarousel.current && isHovered &&
          (<>
          <NavigationLeft element={itemCarousel.current}/>
          <NavigationRight element={itemCarousel.current}/>
          </>
          )
        }
        <div
          className={styles.itemCarousel}
          ref={itemCarousel}
        >
          {showAllElement}
          {itemImageElements}
        </div>
        
      </div>
    </div>
  );
}

const NavigationLeft = ({ element }: { element: HTMLDivElement}) => {
  return (
    <button
      id={styles.navLeft}
      className={styles.navigation}
      onClick={() => scrollElement(element, "left")}
    >
      <FaArrowLeft />
    </button>
  )
}

const NavigationRight = ({ element }: { element: HTMLDivElement}) => {
  return (
    <button
      id={styles.navRight}
      className={styles.navigation}
      onClick={() => scrollElement(element, "right")}
    >
      <FaArrowRight />
    </button>
  )
}

function scrollElement(element: HTMLDivElement, direction: "left" | "right") {
  const sign = direction === "left" ? -1 : 1
  element.scrollBy(0.8 * sign * element.offsetWidth, 0)
}

export default FilterCarousel;
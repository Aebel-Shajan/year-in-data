import { createContext, useContext, useState } from "react";
import styles from "./HeatmapContext.module.css";
interface HeatmapContextType {
  showDetails: boolean;
  setShowDetails: CallableFunction;
}

export const HeatmapContext = createContext<HeatmapContextType | null>(null);

export const HeatmapProvider = ({ children }: { children: React.ReactNode }) => {
  const [showDetails, setShowDetails] = useState(true);

  return (
    <HeatmapContext.Provider value={{ showDetails, setShowDetails }}>
      {children}
    </HeatmapContext.Provider>
  );
};

export const DetailsToggleButton = () => {
  const context = useContext(HeatmapContext);
  if (context === null) {
    throw Error("Context not defined properly.")
  }
  const {showDetails, setShowDetails} = context

  return (
    <div className={styles.container}>
      <p>
        Hide Details: 
      </p>
      <label className={styles.switch}>
      <input 
      className={styles.input}
      type="checkbox" 
      onChange={() => setShowDetails(!showDetails)}
      checked={!showDetails}
      />
      <span className={[styles.round, styles.slider].join(" ")}></span>
    </label>

    </div>
    
  );
}
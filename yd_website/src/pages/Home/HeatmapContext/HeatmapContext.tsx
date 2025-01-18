import { createContext, useContext, useState } from "react";
import styles from "./HeatmapContext.module.css";
interface HeatmapContextType {
  showDetails: boolean;
  setShowDetails: CallableFunction;
}

const HeatmapContext = createContext<HeatmapContextType | null>(null);

export const HeatmapProvider = ({ children }: { children: React.ReactNode }) => {
  const [showDetails, setShowDetails] = useState(true);

  return (
    <HeatmapContext.Provider value={{ showDetails, setShowDetails }}>
      {children}
    </HeatmapContext.Provider>
  );
};

export const useHeatmapContext = () => {
  const context = useContext(HeatmapContext);
  if (context === null) {
    throw Error("Context not defined properly.");
  }
  return context;
};

export const DetailsToggleButton = () => {
  const { showDetails, setShowDetails } = useHeatmapContext();

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
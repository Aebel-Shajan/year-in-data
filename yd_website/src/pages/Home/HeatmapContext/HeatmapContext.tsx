import { createContext, useContext, useState } from "react";

export const HeatmapContext = createContext({ showDetails: true, toggleDetails: () => { } });

export const HeatmapProvider = ({ children }: { children: React.ReactNode }) => {
  const [showDetails, setShowDetails] = useState(true);

  const toggleDetails = () => {
    setShowDetails(prevShow => !prevShow);
  };

  return (
    <HeatmapContext.Provider value={{ showDetails, toggleDetails }}>
      {children}
    </HeatmapContext.Provider>
  );
};

export const DetailsToggleButton = () => {
  const { showDetails, toggleDetails } = useContext(HeatmapContext);

  return (
    <button onClick={toggleDetails}>
      {showDetails ? 'Hide Details' : 'Show Details'}
    </button>
  );
}
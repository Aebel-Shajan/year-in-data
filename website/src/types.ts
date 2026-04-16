export interface DataPoint {
  date: string;      // ISO date string "YYYY-MM-DD"
  value: number;
  category?: string;
  image_url?: string;
}

export interface MetricData {
  asset_name: string;
  metric: string;
  unit: string;
  label: string;
  updated_at: string;
  data: DataPoint[];
}

// A metric descriptor used to configure the data sections on the page
export interface MetricConfig {
  metric: string;
  colorScheme: "greens" | "blues" | "oranges" | "purples" | "reds" | "warm";
}

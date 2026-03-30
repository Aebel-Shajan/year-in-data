import { useCallback, useState } from "react";
import type { MetricConfig } from "./types";
import { DataSection } from "./components/DataSection";

const METRICS: MetricConfig[] = [
  { source: "github",  metric: "contributions", label: "GitHub contributions", colorScheme: "greens"  },
  { source: "fitbit",  metric: "steps",         label: "Steps",                colorScheme: "blues"   },
  { source: "fitbit",  metric: "calories",      label: "Calories burned",      colorScheme: "oranges" },
  { source: "fitbit",  metric: "sleep",         label: "Sleep (hours)",        colorScheme: "purples" },
  { source: "fitbit",  metric: "exercise",      label: "Active minutes",       colorScheme: "reds"    },
  { source: "kindle",  metric: "reading",       label: "Reading (minutes)",    colorScheme: "warm"    },
  { source: "strong",  metric: "workouts",      label: "Workout duration",     colorScheme: "oranges" },
  { source: "gymgroup",    metric: "visits",     label: "Gym visits",           colorScheme: "greens"  },
  { source: "screentime",  metric: "app_usage", label: "Screen time",          colorScheme: "reds"    },
];

export default function App() {
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [availableYears, setAvailableYears] = useState<number[]>([new Date().getFullYear()]);

  const handleYearsLoaded = useCallback((years: number[]) => {
    setAvailableYears((prev) => {
      const merged = [...new Set([...prev, ...years])].sort((a, b) => a - b);
      return merged.length === prev.length && merged.every((y, i) => y === prev[i]) ? prev : merged;
    });
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex flex-col">
      <header className="sticky top-0 z-10 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-6">
          <div>
            <h1 className="text-2xl font-bold leading-none">Year in Data</h1>
            <p className="text-sm text-gray-500 mt-0.5">Personal activity heatmaps</p>
          </div>

          {availableYears.length > 1 && (
            <div className="flex gap-1 ml-6">
              {availableYears.map((y) => (
                <button
                  key={y}
                  onClick={() => setYear(y)}
                  className={`px-2 py-0.5 text-sm rounded transition-colors ${
                    y === year
                      ? "bg-gray-800 text-white dark:bg-gray-200 dark:text-gray-900"
                      : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
                  }`}
                >
                  {y}
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
        {METRICS.map((cfg) => (
          <DataSection
            key={`${cfg.source}/${cfg.metric}`}
            config={cfg}
            year={year}
            onYearsLoaded={handleYearsLoaded}
          />
        ))}
      </main>

      <footer className="border-t border-gray-200 dark:border-gray-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-end gap-3 text-sm text-gray-400">
          <a
            href="https://github.com/Aebel-Shajan/year-in-data"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <GitHubIcon className="w-4 h-4" />
            Aebel-Shajan/year-in-data
          </a>
        </div>
      </footer>
    </div>
  );
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
        0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
        -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
        .07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
        -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27
        .68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12
        .51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
        0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
    </svg>
  );
}

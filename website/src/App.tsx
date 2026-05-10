import { useCallback, useEffect, useState } from "react";
import type { MetricConfig } from "./types";
import { DataSection } from "./components/DataSection";
import { DocsPage } from "./components/DocsPage";

type Tab = "data" | "docs";

const GROUPS: { label: string; metrics: MetricConfig[] }[] = [
  {
    label: "Productivity",
    metrics: [
      { metric: "daily_github_contributions", colorScheme: "greens" },
      { metric: "daily_kindle_reading", colorScheme: "warm" },
      { metric: "daily_macos_screentime", colorScheme: "reds" },
      { metric: "daily_macos_commands", colorScheme: "greens" },
    ],
  },
  {
    label: "Health",
    metrics: [
      { metric: "daily_gymgroup_visits", colorScheme: "greens" },
      { metric: "daily_sleep", colorScheme: "purples" },
      { metric: "daily_steps", colorScheme: "blues" },
      { metric: "daily_exercise", colorScheme: "reds" },
      { metric: "daily_calories", colorScheme: "oranges" },
    ],
  },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("data");
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
      <header className="sticky top-0 z-10 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 px-6 py-2">
        <div className="max-w-5xl mx-auto flex flex-wrap items-center gap-3 justify-between">
          <div className="flex flex-wrap gap-3 w-full justify-between items-center">
            <div className="flex items-center gap-2">
              <img src="favicon.svg" alt="" className="w-7 h-7 rounded-md" />
              <div>
                <a
                  href="https://github.com/Aebel-Shajan/year-in-data"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base font-bold leading-none hover:underline"
                >Year in Data</a>
                <div className="flex items-center gap-2 mt-0.5">
                  <PipelineStatus />
                </div>
              </div>
            </div>
            <nav className="flex gap-1 items-center">
              {(["data", "docs"] as Tab[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`px-3 py-0.5 text-xs rounded transition-colors capitalize ${t === tab
                    ? "bg-gray-800 text-white dark:bg-gray-200 dark:text-gray-900"
                    : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
                    }`}
                >
                  {t}
                </button>
              ))}
            </nav>
          </div>


          <div className="flex items-center gap-4 overflow-x-scroll">

            {tab === "data" && availableYears.length > 1 && (
              <div className="flex gap-1 flex-nowrap">
                {availableYears.map((y) => (
                  <button
                    key={y}
                    onClick={() => setYear(y)}
                    className={`px-2 py-0.5 text-xs rounded transition-colors ${y === year
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
        </div>
      </header>

      {tab === "data" ? (
        <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
          <div className="text-sm text-gray-500 dark:text-gray-400 mb-10 max-w-2xl leading-relaxed space-y-3">
            <p>I wanted to track my habits and have it visualised like github's activity heatmap. However, I was too lazy to use habit tracker apps, so I built this instead.</p>
            <p>It's a Polars data pipeline that runs every week on github actions and processes data stored in cloudflare r2. I don't like paying money for things so I'm leeching off github's free compute and cloudflare's free tier.</p>
            <p>Most of the data is automatic, extracted from apis + a cron job on my macbook. However for reading and payments I still have to manually upload files. Amazon doesn't have a kindle api and makes scraping hard. I could use truelayer for bank transactions but it's a pain to set up so I'm sticking with manually uploading statements.</p>
            <p>It's free and reproducible, feel free to fork it. No guarantees though, I'll probably refactor this again for the 10th time because the code is disgusting and I hate it.</p>
          </div>
          {GROUPS.map((group) => (
            <section key={group.label} className="mb-12">
              <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-6">
                {group.label}
              </h2>
              {group.metrics.map((cfg) => (
                <DataSection
                  key={cfg.metric}
                  config={cfg}
                  year={year}
                  onYearsLoaded={handleYearsLoaded}
                />
              ))}
            </section>
          ))}
        </main>
      ) : (
        <main className="flex-1 w-full">
          <DocsPage />
        </main>
      )}

      <footer className="border-t border-gray-200 dark:border-gray-800 px-6 py-4">
        <div className=" mx-auto flex items-center justify-center gap-10 flex-wrap text-xs text-gray-400">
          <CopyEmail />
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

function CopyEmail() {
  const [copied, setCopied] = useState(false);
  const email = "aebel.projects@gmail.com";

  const handleClick = () => {
    navigator.clipboard.writeText(email).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <button
      onClick={handleClick}
      className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
    >
      {copied ? "copied! send email, I command you 👽" : email}
    </button>
  );
}

function PipelineStatus() {
  const [run, setRun] = useState<{ date: string; url: string; conclusion: string } | null>(null);

  useEffect(() => {
    fetch("https://api.github.com/repos/Aebel-Shajan/year-in-data/actions/workflows/pipeline.yml/runs?per_page=1")
      .then((r) => r.json())
      .then((data) => {
        const latest = data.workflow_runs?.[0];
        if (!latest) return;
        setRun({
          date: new Date(latest.updated_at).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }),
          url: latest.html_url,
          conclusion: latest.conclusion ?? latest.status,
        });
      })
      .catch(() => {});
  }, []);

  if (!run) return null;

  const dot: Record<string, string> = {
    success: "bg-green-500",
    failure: "bg-red-500",
    cancelled: "bg-yellow-500",
  };

  return (
    <a
      href={run.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-1 text-[10px] text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
    >
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dot[run.conclusion] ?? "bg-gray-400"}`} />
      pipeline last run {run.date}
    </a>
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

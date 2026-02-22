import { Button } from "@/components/ui/button";
import { LogPanel } from "@/components/etl/LogPanel";
import { StatusBadge } from "@/components/etl/StatusBadge";
import { useEffect, useState } from "react";
import type { EtlLogEntry, EtlRun } from "src/electron/sharedTypes";

function formatDuration(startedAt: string, finishedAt: string | null): string {
  if (!finishedAt) return "—";
  const ms = new Date(finishedAt).getTime() - new Date(startedAt).getTime();
  if (ms < 1000) return `${ms}ms`;
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}

export default function EtlRunsDashboard() {
  const [runs, setRuns] = useState<EtlRun[]>([]);
  const [expandedRunId, setExpandedRunId] = useState<number | null>(null);
  const [storedLogs, setStoredLogs] = useState<EtlLogEntry[]>([]);
  const [liveLogs, setLiveLogs] = useState<EtlLogEntry[]>([]);

  async function fetchRuns() {
    const data = await window.electronAPI.getEtlRuns();
    setRuns(data);
  }

  // Subscribe to real-time log events
  useEffect(() => {
    window.electronAPI.onEtlLog((entry) => {
      setLiveLogs((prev) => [...prev, entry]);
    });
    return () => {
      window.electronAPI.removeEtlLogListener();
    };
  }, []);

  // Fetch runs on mount
  useEffect(() => {
    fetchRuns();
  }, []);

  // Auto-refresh while any run is in 'running' state
  useEffect(() => {
    const hasRunning = runs.some((r) => r.status === "running");
    if (!hasRunning) return;
    const interval = setInterval(fetchRuns, 2000);
    return () => clearInterval(interval);
  }, [runs]);

  async function toggleRunLogs(run: EtlRun) {
    if (expandedRunId === run.id) {
      setExpandedRunId(null);
      setStoredLogs([]);
      return;
    }
    setExpandedRunId(run.id);
    if (run.status === "running") {
      setStoredLogs([]);
    } else {
      const logs = await window.electronAPI.getEtlRunLogs(run.id);
      setStoredLogs(logs);
    }
  }

  return (
    <div className="w-full h-fit p-3 flex flex-col gap-3">
      <div className="p-3 outline rounded-xl flex items-center justify-between sticky top-3 bg-background">
        <div className="font-extrabold text-2xl">ETL Run History</div>
        <Button variant="outline" onClick={fetchRuns}>
          Refresh
        </Button>
      </div>

      <div className="p-2 outline rounded-xl overflow-auto">
        <table className="w-full text-sm table-fixed">
          <thead>
            <tr className="border-b text-left">
              <th className="p-2">Data Source</th>
              <th className="p-2 w-24">Status</th>
              <th className="p-2">Started</th>
              <th className="p-2 w-24">Duration</th>
              <th className="p-2 w-24">Records</th>
              <th className="p-2">Error</th>
            </tr>
          </thead>
          <tbody>
            {runs.length === 0 && (
              <tr>
                <td colSpan={6} className="p-4 text-center text-muted-foreground">
                  No ETL runs yet. Run an ETL from one of the data source pages.
                </td>
              </tr>
            )}
            {runs.map((run) => {
              const isExpanded = expandedRunId === run.id;
              const isRunning = run.status === "running";
              const displayLogs = isRunning
                ? liveLogs.filter((l) => l.runId === run.id)
                : storedLogs;

              return (
                <>
                  <tr
                    key={run.id}
                    className="border-b cursor-pointer hover:bg-accent/50"
                    onClick={() => toggleRunLogs(run)}
                  >
                    <td className="p-2 font-mono">{run.table_name}</td>
                    <td className="p-2">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="p-2">{new Date(run.started_at).toLocaleString()}</td>
                    <td className="p-2">{formatDuration(run.started_at, run.finished_at)}</td>
                    <td className="p-2">{run.record_count ?? "—"}</td>
                    <td
                      className="p-2 text-red-600 dark:text-red-400 truncate"
                      title={run.error_message ?? undefined}
                    >
                      {run.error_message ?? "—"}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr key={`${run.id}-logs`}>
                      <td colSpan={6} className="p-0">
                        <LogPanel logs={displayLogs} isLive={isRunning} />
                      </td>
                    </tr>
                  )}
                </>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

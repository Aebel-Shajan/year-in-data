import { useEffect, useRef } from "react";
import type { EtlLogEntry } from "src/electron/sharedTypes";

export function LogPanel({ logs, isLive }: { logs: EtlLogEntry[]; isLive: boolean }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isLive && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs.length, isLive]);

  const levelStyles: Record<string, string> = {
    log: "text-foreground",
    error: "text-red-500",
    warn: "text-yellow-500",
  };

  return (
    <div className="bg-accent/30 max-h-64 overflow-y-auto p-3 font-mono text-xs">
      {isLive && (
        <div className="text-yellow-600 dark:text-yellow-400 mb-2 text-xs font-sans font-medium">
          Live log stream...
        </div>
      )}
      {logs.length === 0 && (
        <div className="text-muted-foreground">
          {isLive ? "Waiting for logs..." : "No logs available."}
        </div>
      )}
      {logs.map((entry, i) => (
        <div key={i} className={`py-0.5 ${levelStyles[entry.level] ?? ""}`}>
          <span className="text-muted-foreground mr-2">
            {new Date(entry.timestamp).toLocaleTimeString()}
          </span>
          {entry.level !== "log" && (
            <span className="mr-2 uppercase text-[10px] font-bold opacity-60">
              [{entry.level}]
            </span>
          )}
          {entry.message}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

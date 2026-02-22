import type { EtlRun } from "src/electron/sharedTypes";

export function StatusBadge({ status }: { status: EtlRun["status"] }) {
  const styles: Record<string, string> = {
    success: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    running: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  };
  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] ?? ""}`}>
      {status}
    </span>
  );
}

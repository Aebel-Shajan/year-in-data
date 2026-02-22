import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import { LogPanel } from "./LogPanel";
import { StatusBadge } from "./StatusBadge";
import type { EtlLogEntry, EtlResult, ConfigType } from "src/electron/sharedTypes";

type ModalPhase = "config" | "running" | "done";

interface EtlRunModalProps {
  tableName: string;
  label: string;
  requiresFile: boolean;
  extensions?: string[]
  targetDir?: string;
  onComplete: () => void;
  trigger: React.ReactNode;
}

export function EtlRunModal({
  tableName,
  label,
  requiresFile,
  extensions=[],
  targetDir,
  onComplete,
  trigger,
}: EtlRunModalProps) {
  const [open, setOpen] = useState(false);
  const [phase, setPhase] = useState<ModalPhase>("config");
  const [filePath, setFilePath] = useState<string | null>(null);
  const [logs, setLogs] = useState<EtlLogEntry[]>([]);
  const [result, setResult] = useState<EtlResult | null>(null);

  function resetState() {
    setPhase("config");
    setFilePath(null);
    setLogs([]);
    setResult(null);
  }

  function handleOpenChange(nextOpen: boolean) {
    if (phase === "running") return;
    if (!nextOpen) resetState();
    setOpen(nextOpen);
  }

  async function handleSelectFile() {
    const selected = await window.electronAPI.selectFile(extensions);
    if (selected) setFilePath(selected);
  }

  async function handleRun() {
    setLogs([]);
    setPhase("running");

    window.electronAPI.onEtlLog((entry) => {
      setLogs((prev) => [...prev, entry]);
    });

    const config: ConfigType = {};
    if (requiresFile && filePath && targetDir) {
      config.zipPath = filePath;
      config.targetDir = targetDir;
    }

    const etlResult = await window.electronAPI.runEtl(tableName, config);
    setResult(etlResult);
    setPhase("done");

    window.electronAPI.removeEtlLogListener();

    if (etlResult.success) {
      onComplete();
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent
        className="sm:max-w-2xl"
        showCloseButton={phase !== "running"}
        onPointerDownOutside={(e) => {
          if (phase === "running") e.preventDefault();
        }}
        onEscapeKeyDown={(e) => {
          if (phase === "running") e.preventDefault();
        }}
      >
        <DialogHeader>
          <DialogTitle>Extract {label}</DialogTitle>
          <DialogDescription>
            {phase === "config" &&
              (requiresFile
                ? "Select the data file to process."
                : "Click Run to start extraction.")}
            {phase === "running" && "Extraction in progress..."}
            {phase === "done" &&
              (result?.success
                ? "Extraction complete."
                : "Extraction failed.")}
          </DialogDescription>
        </DialogHeader>

        {phase === "config" && (
          <>
            {requiresFile && (
              <div className="flex w-full gap-2 items-start">
                <Button variant="outline" onClick={handleSelectFile}>
                  Select file
                </Button>
                {filePath && (
                  <div className="font-light font-mono text-sm flex-1 break-all bg-accent p-2 rounded-md">
                    {filePath}
                  </div>
                )}
              </div>
            )}
            <DialogFooter>
              <Button
                onClick={handleRun}
                disabled={requiresFile && !filePath}
              >
                Run
              </Button>
            </DialogFooter>
          </>
        )}

        {phase === "running" && (
          <div className="flex flex-col gap-3">
            <StatusBadge status="running" />
            <LogPanel logs={logs} isLive={true} />
          </div>
        )}

        {phase === "done" && (
          <div className="flex flex-col gap-3">
            <StatusBadge status={result?.success ? "success" : "error"} />
            {!result?.success && result?.runMetadata?.message && (
              <div className="text-red-600 dark:text-red-400 text-sm">
                {String(result.runMetadata.message)}
              </div>
            )}
            <LogPanel logs={logs} isLive={false} />
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">Close</Button>
              </DialogClose>
            </DialogFooter>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

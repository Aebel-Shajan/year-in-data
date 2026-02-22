
// duplicated in multiple places
export interface EtlResult {
  success: boolean,
  runId?: number,
  runMetadata: Record<string, string | number>
}

export interface EtlLogEntry {
  timestamp: string
  level: 'log' | 'error' | 'warn'
  message: string
  runId: number
}

export interface EtlRun {
  id: number
  table_name: string
  status: 'success' | 'error' | 'running'
  started_at: string
  finished_at: string | null
  record_count: number | null
  error_message: string | null
  config: string | null
  logs: string | null
}

export interface IpcAPI {
  runEtl(tableName: string, config: ConfigType): Promise<EtlResult>
  getDataByYear: (tableName: string, year: number, dateColumn: string) => Promise<Record<string, string | number>[]>
  getEtlRuns(): EtlRun[] | Promise<EtlRun[]>
  getEtlRunLogs(runId: number): EtlLogEntry[] | Promise<EtlLogEntry[]>
  selectFile(extensions: string[]):  Promise<string | null>
  showDialogError: (message: string) => void
}

export interface IpcRendererAPI extends IpcAPI {
  onEtlLog: (callback: (entry: EtlLogEntry) => void) => void
  removeEtlLogListener: () => void
}

export type ConfigType = Record<string, string|number>

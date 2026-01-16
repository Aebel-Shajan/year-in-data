
// duplicated in multiple places
export interface EtlResult {
  success: boolean,
  runMetadata: Record<string, string | number>
}
export interface IpcAPI {
  runEtl(tableName: string, config: ConfigType): Promise<EtlResult>
  getDataByYear: (tableName: string, year: number, dateColumn: string) => Promise<Record<string, string | number>[]>
  selectFile(): Promise<string | null>
  showDialogError: (message: string) => void
}

export type ConfigType = Record<string, string|number>

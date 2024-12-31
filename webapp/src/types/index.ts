export interface HistoryItem {
    image: string
    prompt: string
    type: 'generate' | 'edit' | 'upload' | 'replace'
    timestamp: number
}

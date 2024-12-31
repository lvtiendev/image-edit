export interface HistoryItem {
    image: string
    prompt: string
    type: 'generate' | 'edit'
    timestamp: number
}

'use client'

import { HistoryItem } from '@/types'

interface HistoryPanelProps {
    history: HistoryItem[]
    onSelect: (image: string) => void
}

export default function HistoryPanel({ history, onSelect }: HistoryPanelProps) {
    const getTypeIcon = (type: HistoryItem['type']) => {
        switch (type) {
            case 'generate': return '🎨 Generated'
            case 'edit': return '✏️ Edited'
            case 'upload': return '📤 Uploaded'
            case 'replace': return '🔄 Replaced'
            default: return '❓ Unknown'
        }
    }

    return (
        <div className="h-1/3 p-4 bg-white rounded-lg shadow-lg m-4 overflow-auto">
            <h2 className="text-lg font-semibold mb-4">History</h2>
            <div className="space-y-4">
                {history.map((item) => (
                    <div
                        key={item.timestamp}
                        className="flex items-center space-x-4 p-2 hover:bg-gray-100 rounded cursor-pointer"
                        onClick={() => onSelect(item.image)}
                    >
                        <div>
                            <p className="text-sm font-medium">{getTypeIcon(item.type)}</p>
                            <p className="text-sm text-gray-600 truncate max-w-xs">{item.prompt}</p>
                            <p className="text-xs text-gray-400">
                                {new Date(item.timestamp).toLocaleTimeString()}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

'use client'

import { useState } from 'react'
import ImagePanel from '@/components/ImagePanel'
import ChatPanel from '@/components/ChatPanel'
import HistoryPanel from '@/components/HistoryPanel'
import { HistoryItem } from '@/types'

export default function AIImageEditor() {
  const [currentImage, setCurrentImage] = useState<string | null>(null)
  const [imageHistory, setImageHistory] = useState<HistoryItem[]>([])

  const handleImageUploaded = (imageEncoded: string, event: 'upload' | 'replace') => {
    setCurrentImage(imageEncoded)
    setImageHistory(prev => [...prev, {
      image: imageEncoded,
      prompt: event == 'upload' ? 'Uploaded image' : 'Replaced image',
      type: event,
      timestamp: Date.now()
    }])
  }

  const handleImageGenerated = (imageEncoded: string, prompt: string) => {
    setCurrentImage(imageEncoded)
    setImageHistory(prev => [...prev, {
      image: imageEncoded,
      prompt,
      type: 'generate',
      timestamp: Date.now()
    }])
  }

  const handleImageEdited = (imageEncoded: string, prompt: string) => {
    setCurrentImage(imageEncoded)
    setImageHistory(prev => [...prev, {
      image: imageEncoded,
      prompt,
      type: 'edit',
      timestamp: Date.now()
    }])
  }

  const handleHistorySelect = (imageEncoded: string) => {
    setCurrentImage(imageEncoded)
  }

  return (
    <main className="flex h-screen bg-gray-100">
      <div className="flex-1 flex flex-col">
        <ImagePanel
          currentImage={currentImage}
          onImageUploaded={handleImageUploaded}
        />
        <HistoryPanel
          history={imageHistory}
          onSelect={handleHistorySelect}
        />
      </div>
      <ChatPanel
        onImageGenerated={(image: string, prompt: string) => handleImageGenerated(image, prompt)}
        onImageEdited={(image: string, prompt: string) => handleImageEdited(image, prompt)}
        currentImage={currentImage}
      />
    </main>
  )
}

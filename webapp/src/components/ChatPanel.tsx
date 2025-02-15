'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useChat } from 'ai/react'

interface ChatPanelProps {
    onImageGenerated: (imageUrl: string, prompt: string) => void
    onImageEdited: (imageUrl: string, prompt: string) => void
    currentImage: string | null
}

const API_URL = process.env.NEXT_PUBLIC_IMAGE_SERVER_URL || 'http://localhost:8000'

export default function ChatPanel({ onImageGenerated, onImageEdited, currentImage }: ChatPanelProps) {
    const [isGenerating, setIsGenerating] = useState(false)
    const { messages, input, handleInputChange, setMessages } = useChat()

    const handleGenerateImage = async (prompt: string) => {
        setIsGenerating(true)
        try {
            const response = await fetch(`${API_URL}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "prompt": prompt,
                    "negative_prompt": "blur, distortion",
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5,
                }),
            })

            if (!response.ok) throw new Error('Failed to generate image')

            const data = await response.json()
            const imageEncoded = data.image
            onImageGenerated(imageEncoded, prompt)
            setMessages(prev => [...prev, { id: String(Date.now()), role: "assistant", content: 'Image generated successfully!' }])
        } catch (error) {
            console.error('Error generating image:', error)
            setMessages(prev => [...prev, { id: String(Date.now()), role: "assistant", content: 'Failed to generate image. Please try again.' }])
        }
        setIsGenerating(false)
    }

    const handleEditImage = async (prompt: string) => {
        if (!currentImage) {
            setMessages(prev => [...prev, {
                id: String(Date.now()),
                role: "assistant",
                content: 'Please upload an image first before editing.'
            }])
            return
        }

        setIsGenerating(true)
        try {
            // Convert base64 to blob
            const byteCharacters = atob(currentImage)
            const byteNumbers = new Array(byteCharacters.length)
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i)
            }
            const byteArray = new Uint8Array(byteNumbers)
            const imageBlob = new Blob([byteArray], { type: 'image/png' })

            // Create FormData and append fields
            const formData = new FormData()
            formData.append('file', imageBlob, 'image.png')
            formData.append('prompt', prompt)
            formData.append('strength', '0.75')

            const response = await fetch(`${API_URL}/edit`, {
                method: 'POST',
                body: formData
            })

            if (!response.ok) throw new Error('Failed to edit image')

            const data = await response.json()
            const imageEncoded = data.image
            onImageEdited(imageEncoded, prompt)
            setMessages(prev => [...prev, {
                id: String(Date.now()),
                role: "assistant",
                content: 'Image edited successfully!'
            }])
        } catch (error) {
            console.error('Error editing image:', error)
            setMessages(prev => [...prev, {
                id: String(Date.now()),
                role: "assistant",
                content: 'Failed to edit image. Please try again.'
            }])
        }
        setIsGenerating(false)
    }

    const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        if (isGenerating) return

        setMessages(prev => [...prev, {
            id: String(Date.now()),
            role: "user",
            content: input
        }])

        if (input.toLowerCase().startsWith('generate:')) {
            await handleGenerateImage(input.slice(9).trim())
        } else {
            await handleEditImage(input.trim())
        }
    }

    return (
        <div className="w-1/3 p-4 bg-white rounded-lg shadow-lg m-4 flex flex-col">
            <ScrollArea className="flex-1 mb-4">
                {messages.map((message, i) => (
                    <div key={i} className={`mb-4 ${message.role === 'user' ? 'text-blue-600' : 'text-green-600'}`}>
                        <strong>{message.role === 'user' ? 'You: ' : 'AI: '}</strong>
                        {message.content}
                    </div>
                ))}
            </ScrollArea>
            <form onSubmit={handleFormSubmit} className="flex space-x-2">
                <Input
                    value={input}
                    onChange={handleInputChange}
                    placeholder={isGenerating ? 'Generating...' : 'Type a message...'}
                    disabled={isGenerating}
                />
                <Button type="submit" disabled={isGenerating}>Send</Button>
            </form>
        </div>
    )
}

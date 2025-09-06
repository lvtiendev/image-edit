'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useChat } from 'ai/react'
import { HelpCircle } from 'lucide-react'

interface ChatPanelProps {
    onImageGenerated: (imageUrl: string, prompt: string) => void
    onImageEdited: (imageUrl: string, prompt: string) => void
    currentImage: string | null
}

const API_URL = process.env.NEXT_PUBLIC_IMAGE_SERVER_URL || 'http://localhost:8000'

export default function ChatPanel({ onImageGenerated, onImageEdited, currentImage }: ChatPanelProps) {
    const [isGenerating, setIsGenerating] = useState(false)
    const [showTooltip, setShowTooltip] = useState(false)
    const [serverStatus, setServerStatus] = useState<'checking' | 'connected' | 'error'>('checking')
    const { messages, input, handleInputChange, setMessages } = useChat()

    // Check server connection on component mount
    React.useEffect(() => {
        const checkServerConnection = async () => {
            try {
                console.log('Checking server connection to:', API_URL)
                const response = await fetch(`${API_URL}/health`)
                if (response.ok) {
                    const data = await response.json()
                    console.log('Server health check:', data)
                    setServerStatus('connected')
                } else {
                    console.error('Server health check failed:', response.status)
                    setServerStatus('error')
                }
            } catch (error) {
                console.error('Server connection error:', error)
                setServerStatus('error')
            }
        }
        checkServerConnection()
    }, [])

    const handleGenerateImage = async (prompt: string) => {
        setIsGenerating(true)
        try {
            console.log('Generating image with prompt:', prompt, 'API URL:', API_URL)
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

            if (!response.ok) {
                const errorText = await response.text()
                console.error('Generate API error:', response.status, errorText)
                throw new Error(`Server error: ${response.status} - ${errorText}`)
            }

            const data = await response.json()
            const imageEncoded = data.image
            onImageGenerated(imageEncoded, prompt)
            setMessages(prev => [...prev, { id: String(Date.now()), role: "assistant", content: 'Image generated successfully!' }])
        } catch (error) {
            console.error('Error generating image:', error)
            const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
            setMessages(prev => [...prev, { id: String(Date.now()), role: "assistant", content: `Failed to generate image: ${errorMessage}` }])
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

        if (input.toLowerCase().startsWith('/generate ')) {
            await handleGenerateImage(input.slice(10).trim())
        } else if (input.toLowerCase().startsWith('/edit ')) {
            await handleEditImage(input.slice(6).trim())
        } else {
            // Default to edit if no command prefix
            await handleEditImage(input.trim())
        }
    }

    return (
        <div className="w-1/3 p-4 bg-white rounded-lg shadow-lg m-4 flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Chat</h3>
                <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${serverStatus === 'connected' ? 'bg-green-500' :
                        serverStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                        }`}></div>
                    <span className="text-xs text-gray-500">
                        {serverStatus === 'connected' ? 'Server Connected' :
                            serverStatus === 'error' ? 'Server Error' : 'Connecting...'}
                    </span>
                </div>
                <div className="relative">
                    <button
                        onMouseEnter={() => setShowTooltip(true)}
                        onMouseLeave={() => setShowTooltip(false)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="Help"
                    >
                        <HelpCircle size={20} />
                    </button>
                    {showTooltip && (
                        <div className="absolute right-0 top-8 w-80 bg-gray-900 text-white text-sm rounded-lg p-4 shadow-lg z-50">
                            <div className="space-y-2">
                                <div className="font-semibold">How to use the chat:</div>
                                <div>
                                    <span className="font-medium text-blue-300">Generate images:</span>
                                    <br />
                                    Type <code className="bg-gray-700 px-1 rounded">/generate your prompt here</code>
                                    <br />
                                    <span className="text-gray-300 text-xs">Example: /generate a beautiful sunset over mountains</span>
                                </div>
                                <div>
                                    <span className="font-medium text-green-300">Edit images:</span>
                                    <br />
                                    Upload an image first, then type <code className="bg-gray-700 px-1 rounded">/edit your prompt</code>
                                    <br />
                                    <span className="text-gray-300 text-xs">Example: /edit make it more colorful, add a cat</span>
                                </div>
                                <div>
                                    <span className="text-gray-300 text-xs">Or just type your prompt without a command to edit the current image</span>
                                </div>
                            </div>
                            <div className="absolute -top-1 right-4 w-2 h-2 bg-gray-900 transform rotate-45"></div>
                        </div>
                    )}
                </div>
            </div>
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

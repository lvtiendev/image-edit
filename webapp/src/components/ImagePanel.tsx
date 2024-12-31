'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Upload } from 'lucide-react'

interface ImagePanelProps {
    currentImage: string | null
    onImageUploaded: (encodedImage: string, event: 'upload' | 'replace') => void
}

export default function ImagePanel({ currentImage, onImageUploaded }: ImagePanelProps) {
    const [isUploading, setIsUploading] = useState(false)

    // Helper function to format base64 string
    const formatBase64Image = (base64String: string) => {
        // Remove any whitespace or line breaks
        const cleanString = base64String.trim()
        // Add data URL prefix if it doesn't exist
        return cleanString.startsWith('data:image')
            ? cleanString
            : `data:image/jpeg;base64,${cleanString}`
    }

    const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file) return

        setIsUploading(true)

        try {
            const reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onload = () => {
                if (typeof reader.result === 'string') {
                    // Extract just the base64 part by removing the data URL prefix
                    const base64String = reader.result.split(',')[1]
                    const event = currentImage ? 'replace' : 'upload'
                    onImageUploaded(base64String, event)
                    setIsUploading(false)
                }
            }
            reader.onerror = (error) => {
                console.error('Error reading file:', error)
                setIsUploading(false)
            }
        } catch (error) {
            console.error('Error uploading image:', error)
            setIsUploading(false)
            return
        }
    }

    return (
        <div className="flex-1 p-4 flex flex-col items-center justify-center bg-white rounded-lg shadow-lg m-4">
            {currentImage && (
                <img
                    src={formatBase64Image(currentImage)}
                    alt="Current"
                    className="max-w-full max-h-[80%] object-contain mb-4"
                />
            )}
            <div className="text-center">
                <Button disabled={isUploading}>
                    <label className="cursor-pointer flex items-center">
                        <Upload className="mr-2" />
                        {isUploading ? 'Uploading...' : (currentImage ? 'Replace Image' : 'Upload Image')}
                        <input
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleImageUpload}
                            disabled={isUploading}
                        />
                    </label>
                </Button>
            </div>
        </div>
    )
}

'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Upload } from 'lucide-react'

interface ImagePanelProps {
    currentImage: string | null
    onImageUploaded: (imageUrl: string, prompt: string) => void
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
        // Here you would typically upload the file to your server or a cloud storage service
        // For this example, we'll just create a local URL
        const imageUrl = URL.createObjectURL(file)
        onImageUploaded(imageUrl, 'Uploaded image')
        setIsUploading(false)
    }

    return (
        <div className="flex-1 p-4 flex items-center justify-center bg-white rounded-lg shadow-lg m-4">
            {currentImage ? (
                <img
                    src={formatBase64Image(currentImage)}
                    alt="Current"
                    className="max-w-full max-h-full object-contain"
                />
            ) : (
                <div className="text-center">
                    <Button disabled={isUploading}>
                        <label className="cursor-pointer flex items-center">
                            <Upload className="mr-2" />
                            {isUploading ? 'Uploading...' : 'Upload Image'}
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
            )}
        </div>
    )
}

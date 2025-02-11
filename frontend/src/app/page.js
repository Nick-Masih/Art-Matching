'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)  // For modal

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    setSelectedFile(file)
    setPreview(URL.createObjectURL(file))
    setError(null) // Clear any previous errors
  }

  const handleSubmit = async () => {
    if (!selectedFile) return

    setLoading(true)
    setError(null)
    const formData = new FormData()
    formData.append('image', selectedFile)

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Something went wrong')
      }
      
      const data = await response.json()
      setResults(data.results)
    } catch (error) {
      setError(error.message || 'An error occurred while processing your request')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="flex flex-col items-center space-y-8">
        <style jsx global>{`
          @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
          
          .animate-gradient {
            background-size: 200% 200%;
            animation: gradient 8s ease infinite;
          }
        `}</style>

        <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-gray-500 to-white bg-clip-text text-transparent animate-gradient">
          Art Matching
        </h1>
        
        {/* Upload Section */}
        <div className="w-full max-w-md">
          <label 
            htmlFor="file-upload"
            className="block w-full px-4 py-3 mb-4 text-center rounded-lg cursor-pointer bg-gradient-to-r from-gray-900 via-gray-500 to-gray-900 text-white hover:opacity-90 transition-all duration-200 shadow-md hover:shadow-lg animate-gradient"
          >
            Upload Image
            <input
              id="file-upload"
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </label>

          {preview && (
            <div className="relative h-[300px] w-full mb-4">
              <Image 
                src={preview}
                alt="Preview"
                fill
                className="object-contain"
              />
            </div>
          )}
          <button 
            onClick={handleSubmit}
            disabled={!selectedFile || loading}
            className="w-full px-4 py-3 rounded-lg bg-gradient-to-r from-gray-900 via-gray-500 to-gray-900 text-white hover:opacity-90 transition-all duration-200 shadow-md hover:shadow-lg disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed animate-gradient"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching...
              </span>
            ) : 'Find Similar Paintings'}
          </button>
          
          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {results.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-7xl mx-auto">
            {results.map((painting, index) => (
              <div 
                key={index}
                className={`border rounded-lg p-6 shadow overflow-hidden relative flex flex-col h-[600px] ${
                  // For the last two items when there are 5 items (or any number where 2 remain)
                  results.length % 3 === 2 && index === results.length - 2
                    ? 'lg:translate-x-[50%]' // Move halfway into the next column
                    : results.length % 3 === 2 && index === results.length - 1
                    ? 'lg:translate-x-[50%]' // Move halfway into the next column
                    : ''
                } ${
                  // For medium screens (2 columns)
                  index === results.length - 1 && results.length % 2 === 1 
                    ? 'md:col-span-2 lg:col-span-1' 
                    : ''
                }`}
              >
                {/* Background blurred image */}
                <div 
                  className="absolute inset-0 bg-cover bg-center blur-sm opacity-30 scale-110"
                  style={{
                    backgroundImage: `url(${painting.imageBlob || painting.image_url})`,
                  }}
                />
                
                {/* Main image container */}
                <div 
                  className="relative h-[400px] w-full cursor-pointer flex-shrink-0"
                  onClick={() => setSelectedImage(painting)}
                >
                  <Image 
                    src={painting.imageBlob || painting.image_url}
                    alt={painting.title || 'Unknown Artwork'}
                    fill
                    className="object-contain rounded"
                    unoptimized
                    loading="eager"
                    priority={index < 6}
                  />
                </div>

                <div className="relative mt-4 flex-shrink-0 h-[140px] flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-lg truncate">
                      {painting.title ? painting.title : <span className="italic">Title Unknown</span>}
                    </h3>
                    <p className="truncate">
                      {painting.artist ? painting.artist : <span className="italic">Artist Unknown</span>}
                    </p>
                    <p className="truncate">
                      {painting.date ? painting.date : <span className="italic">Date Unknown</span>}
                    </p>
                    <p>Similarity: {(painting.score * 100).toFixed(2)}%</p>
                  </div>
                  <a 
                    href={painting.met_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline block truncate mt-2"
                  >
                    View on Met Website
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Image Modal */}
        {selectedImage && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedImage(null)}
          >
            <div 
              className="relative w-full max-w-4xl h-[80vh] bg-white rounded-lg p-4 overflow-hidden"
              onClick={e => e.stopPropagation()}  // Prevent closing when clicking image
            >
              {/* Background blurred image */}
              <div 
                className="absolute inset-0 bg-cover bg-center blur-sm opacity-30 scale-110"
                style={{
                  backgroundImage: `url(${selectedImage.imageBlob || selectedImage.image_url})`,
                }}
              />
              
              <button
                className="absolute top-2 right-2 z-10 bg-white rounded-full p-2 hover:bg-gray-100"
                onClick={() => setSelectedImage(null)}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-6 w-6" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M6 18L18 6M6 6l12 12" 
                  />
                </svg>
              </button>
              <div className="relative w-full h-full">
                <Image
                  src={selectedImage.imageBlob || selectedImage.image_url}
                  alt={selectedImage.title || 'Artwork'}
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
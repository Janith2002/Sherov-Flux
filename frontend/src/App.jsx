import { useState } from 'react'
import axios from 'axios'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [videoData, setVideoData] = useState(null)
  const [error, setError] = useState('')

  const handleDownload = async () => {
    if (!url) return
    setLoading(true)
    setError('')
    setVideoData(null)

    try {
      // Use environment variable for API URL or fallback to localhost
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${API_URL}/api/download`, { url })
      setVideoData(response.data)
    } catch (err) {
      console.error(err)
      setError('Failed to fetch video. Please check the URL.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-sherov-neon/20 rounded-full blur-[100px]"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-sherov-purple/20 rounded-full blur-[100px]"></div>

      <h1 className="text-4xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-sherov-neon to-sherov-purple mb-8 z-10 font-sans tracking-tight text-center px-2 leading-tight">
        SHEROV FLUX
      </h1>

      <div className="glass p-4 md:p-8 rounded-2xl w-full max-w-2xl z-10">
        <div className="relative flex items-center bg-black/40 border border-white/20 rounded-xl p-1.5 md:p-2 focus-within:border-sherov-neon transition-all">
          <input
            type="text"
            placeholder="Paste Link..."
            className="flex-1 bg-transparent border-none px-3 py-3 text-white placeholder-gray-400 focus:outline-none text-sm md:text-base min-w-0"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />

          <div className="flex items-center gap-2">
            {/* Paste Button */}
            {!url && (
              <button
                onClick={async () => {
                  try {
                    const text = await navigator.clipboard.readText();
                    setUrl(text);
                  } catch (err) {
                    console.error('Failed to read clipboard', err);
                  }
                }}
                className="text-gray-400 hover:text-white text-sm font-medium px-2 md:px-3 py-2 rounded-lg hover:bg-white/10 transition-colors"
                title="Paste Link"
              >
                <span className="hidden sm:inline">PASTE</span>
                <svg className="w-5 h-5 sm:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </button>
            )}

            {/* Download Button */}
            <button
              onClick={handleDownload}
              disabled={loading}
              className="bg-gradient-to-r from-sherov-neon to-sherov-purple text-black font-bold px-4 md:px-6 py-2.5 md:py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center min-w-[80px] md:min-w-[100px] text-sm md:text-base whitespace-nowrap"
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : 'Download'}
            </button>
          </div>
        </div>

        {error && <p className="text-red-400 mt-4 text-center">{error}</p>}

        {videoData && (
          <div className="mt-8 animate-fade-in w-full">
            <div className="flex flex-col md:flex-row gap-6">
              <img
                src={videoData.thumbnail}
                alt={videoData.title}
                className="w-full md:w-1/2 rounded-lg object-cover shadow-lg border border-white/10"
              />
              <div className="flex flex-col justify-between w-full">
                <div>
                  <h2 className="text-xl font-bold mb-2 line-clamp-2 text-white">{videoData.title}</h2>
                  <p className="text-gray-400 text-sm mb-4">Duration: {videoData.duration}</p>
                </div>

                <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                  <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Available Formats</h3>
                  {videoData.formats && videoData.formats.length > 0 ? (
                    videoData.formats.map((format, index) => (
                      <a
                        key={index}
                        href={format.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between bg-white/5 hover:bg-white/10 border border-white/10 p-3 rounded-lg transition-all group"
                      >
                        <span className="flex items-center gap-2">
                          {format.quality === 'audio' ? (
                            <span className="bg-sherov-purple/20 text-sherov-purple px-2 py-1 rounded text-xs font-bold">AUDIO</span>
                          ) : format.quality === '4k' ? (
                            <span className="bg-sherov-neon/20 text-sherov-neon px-2 py-1 rounded text-xs font-bold border border-sherov-neon/50 shadow-[0_0_10px_rgba(0,243,255,0.3)]">
                              4K ULTRA
                            </span>
                          ) : format.quality === '2k' ? (
                            <span className="bg-sherov-neon/20 text-sherov-neon px-2 py-1 rounded text-xs font-bold">
                              2K QHD
                            </span>
                          ) : format.quality === 'hd' ? (
                            <span className="bg-sherov-neon/20 text-sherov-neon px-2 py-1 rounded text-xs font-bold">
                              {format.label.includes('Full HD') ? 'FULL HD' : 'HD'}
                            </span>
                          ) : (
                            <span className="bg-gray-500/20 text-gray-300 px-2 py-1 rounded text-xs font-bold">SD</span>
                          )}
                          <span className="text-sm font-medium text-white">{format.label}</span>
                          {format.file_size && (
                            <span className="text-xs text-sherov-neon ml-2 opacity-90">• {format.file_size}</span>
                          )}
                        </span>
                        <svg className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                        </svg>
                      </a>
                    ))
                  ) : (
                    <p className="text-gray-400 text-sm">No specific formats found. Try the direct link below.</p>
                  )}

                  {/* Fallback direct link if no formats (legacy support) */}
                  {!videoData.formats && videoData.url && (
                    <a
                      href={videoData.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-white/10 hover:bg-white/20 text-white border border-white/20 py-3 rounded-lg text-center font-medium transition-all block"
                    >
                      Download Video
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4 z-10 w-full max-w-4xl text-center">
        {['YouTube', 'TikTok', 'Instagram', 'Facebook'].map((platform) => (
          <div key={platform} className="glass p-4 rounded-xl text-gray-300 text-sm font-medium">
            {platform}
          </div>
        ))}
      </div>
      <div className="mt-12 w-full max-w-4xl text-center z-10">
        <h2 className="text-2xl font-bold text-white mb-6">How to Download</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass p-6 rounded-xl hover:bg-white/5 transition-colors">
            <div className="w-12 h-12 bg-sherov-neon/20 rounded-full flex items-center justify-center mx-auto mb-4 text-sherov-neon text-xl font-bold">1</div>
            <h3 className="text-lg font-semibold text-white mb-2">Copy Link</h3>
            <p className="text-gray-400 text-sm">Copy the video URL from YouTube, TikTok, Instagram, or Facebook.</p>
          </div>
          <div className="glass p-6 rounded-xl hover:bg-white/5 transition-colors">
            <div className="w-12 h-12 bg-sherov-purple/20 rounded-full flex items-center justify-center mx-auto mb-4 text-sherov-purple text-xl font-bold">2</div>
            <h3 className="text-lg font-semibold text-white mb-2">Paste & Search</h3>
            <p className="text-gray-400 text-sm">Click the <b>PASTE</b> button or drop the link, then hit Download.</p>
          </div>
          <div className="glass p-6 rounded-xl hover:bg-white/5 transition-colors">
            <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-green-400 text-xl font-bold">3</div>
            <h3 className="text-lg font-semibold text-white mb-2">Save File</h3>
            <p className="text-gray-400 text-sm">Choose your preferred quality (Audio, HD, 4K) and save it instantly.</p>
          </div>
        </div>
      </div>

      <p className="text-gray-500 text-sm mt-8 pb-8 z-10">
        Compatible with iOS, Android, Windows, and macOS.
      </p>
    </div>
  )
}

export default App

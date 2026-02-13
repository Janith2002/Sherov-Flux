from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from extractors import VideoExtractorManager
from cachetools import TTLCache
import hashlib

# Optional DNS patch for Hugging Face Spaces
try:
    import patch_dns
    patch_dns.patch()
except ImportError:
    print("INFO: patch_dns not found, skipping DNS patch")

app = FastAPI(title="Sherov Flux Video Downloader", version="2.0")

# Configure CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for video info (5 minute TTL, max 100 items)
cache = TTLCache(maxsize=100, ttl=300)

# Initialize extractor manager
extractor_manager = VideoExtractorManager()


class VideoRequest(BaseModel):
    url: str


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Sherov Flux Backend",
        "version": "2.0",
        "features": ["Cobalt API", "yt-dlp", "Auto-fallback"]
    }


@app.get("/api/health")
async def detailed_health():
    """Detailed health check with service status"""
    import httpx
    
    status = {
        "backend": "operational",
        "cobalt_api": "checking...",
        "ytdlp": "operational"
    }
    
    # Check Cobalt API
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("https://api.cobalt.tools/")
            status["cobalt_api"] = "operational" if response.status_code == 200 else "degraded"
    except:
        status["cobalt_api"] = "unavailable"
    
    return status


@app.post("/api/download")
async def extract_video_info(video_request: VideoRequest):
    """
    Extract video information from URL
    
    Supports: YouTube, TikTok, Instagram, Facebook, Twitter, Reddit
    Uses: Cobalt API (primary for social media) + yt-dlp (fallback)
    """
    
    url = video_request.url.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Check cache
    cache_key = hashlib.md5(url.encode()).hexdigest()
    if cache_key in cache:
        print(f"✓ Cache hit for {url}")
        return cache[cache_key]
    
    try:
        print(f"\n{'='*60}")
        print(f"Processing URL: {url}")
        print(f"{'='*60}")
        
        # Extract using multi-strategy manager
        video_data = await extractor_manager.extract(url)
        
        # Validate response
        if not video_data or not video_data.get('formats'):
            raise HTTPException(
                status_code=400, 
                detail="No downloadable formats found. The video might be private or unavailable."
            )
        
        # Cache the result
        cache[cache_key] = video_data
        
        print(f"✓ Successfully extracted {len(video_data['formats'])} formats")
        return video_data
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Extraction failed: {error_msg}")
        
        # User-friendly error messages
        if "private" in error_msg.lower():
            detail = "This video is private and cannot be downloaded"
        elif "unavailable" in error_msg.lower():
            detail = "This video is unavailable or has been deleted"
        elif "age" in error_msg.lower():
            detail = "Age-restricted videos are not supported"
        elif "All extraction methods failed" in error_msg:
            detail = "Unable to download from this platform. Please try a different URL."
        else:
            detail = f"Failed to extract video: {error_msg}"
        
        raise HTTPException(status_code=400, detail=detail)


@app.get("/api/clear-cache")
async def clear_cache():
    """Clear the video info cache (admin endpoint)"""
    cache.clear()
    return {"status": "ok", "message": "Cache cleared"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

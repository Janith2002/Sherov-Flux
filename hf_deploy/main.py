from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import uvicorn
import subprocess
import shlex

import shlex
try:
    import patch_dns
    patch_dns.patch()
except ImportError:
    print("WARNING: patch_dns module not found, skipping custom DNS patch.")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("--------------------------------------------------")
    print("🚀 STARTUP: SHEROV BACKEND V3 (DoH Patch)")
    print(f"📦 yt-dlp version: {yt_dlp.version.__version__}")
    print("✅ /api/debug endpoint should be available")
    print("--------------------------------------------------")
    import patch_dns
    # Ensure patch is applied if not already (it's idempotent-ish)
    patch_dns.patch()

@app.get("/api/debug")
async def debug_network():
    import socket
    import requests
    
    results = {}
    
    # Check 1: System DNS
    try:
        results["system_dns_google"] = socket.gethostbyname("google.com")
    except Exception as e:
        results["system_dns_google"] = str(e)
        
    try:
        results["system_dns_youtube"] = socket.gethostbyname("www.youtube.com")
    except Exception as e:
        results["system_dns_youtube"] = str(e)

    # Check 2: DoH Patch Internal
    try:
        if hasattr(requests, 'packages'):
            requests.packages.urllib3.disable_warnings()
        
        # Test request to Google DNS IP
        r = requests.get("https://8.8.8.8", timeout=2, verify=False)
        results["connect_8888_https"] = r.status_code
    except Exception as e:
        results["connect_8888_https"] = str(e)

    # Check 3: External Connectivity
    try:
        r = requests.get("https://www.google.com", timeout=5)
        results["connect_google_https"] = r.status_code
    except Exception as e:
        results["connect_google_https"] = str(e)

    return results

# Configure CORS
# Configure CORS
origins = [
    "*", # Allow all origins for production (Netlify/Vercel)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/api/stream")
async def stream_video(url: str = Query(...), quality: str = Query(None), type: str = Query("video")):
    # Determine yt-dlp path relative to venv
    import sys
    import os
    
    # Use python -m yt_dlp to avoid path issues on Linux/Docker
    # This works because yt-dlp is installed as a python package
    
    # Build yt-dlp command to stream to stdout
    cmd = [sys.executable, "-m", "yt_dlp", url, "-o", "-", "--quiet", "--no-warnings", "--force-ipv4"]
    
    if type == "audio":
        cmd.extend(["-f", "bestaudio/best", "-x", "--audio-format", "mp3"])
        filename = "audio.mp3"
        media_type = "audio/mpeg"
    else:
        # Video
        if quality:
            cmd.extend(["-f", f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best"])
        
        filename = f"video_{quality or 'best'}.mp4"
        media_type = "video/mp4"

    # streaming generator
    def iterfile():
        # Use subprocess to capture stdout
        # Note: In production, consider using asyncio subprocess
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8) as proc:
            while True:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                yield chunk
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    
    
    return StreamingResponse(iterfile(), media_type=media_type, headers=headers)

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "Sherov Backend"}

@app.get("/api/cobalt-audio")
async def cobalt_audio(url: str = Query(...)):
    """Get audio-only download URL using Cobalt API."""
    try:
        cobalt_url = "https://api.cobalt.tools/"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "downloadMode": "audio",
            "audioFormat": "mp3",
            "audioBitrate": "320"
        }
        
        response = requests.post(cobalt_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Cobalt API error: {response.status_code}")
        
        cobalt_data = response.json()
        
        if cobalt_data.get("status") == "error":
            error_msg = cobalt_data.get("error", {}).get("code", "Unknown error")
            raise HTTPException(status_code=400, detail=f"Cobalt error: {error_msg}")
        
        download_url = cobalt_data.get("url")
        if not download_url:
            raise HTTPException(status_code=400, detail="No download URL from Cobalt")
        
        # Redirect to the audio file
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=download_url)
        
    except Exception as e:
        print(f"Error getting audio: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Audio extraction failed: {str(e)}")

@app.post("/api/download")
async def extract_video_info(video_request: VideoRequest, request: Request):
    """Extract video info using Cobalt API to bypass bot detection."""
    
    try:
        print(f"Processing URL via Cobalt API: {video_request.url}")
        
        # Call Cobalt API
        cobalt_url = "https://api.cobalt.tools/"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": video_request.url,
            "videoQuality": "max",
            "audioFormat": "mp3",
            "filenameStyle": "basic"
        }
        
        response = requests.post(cobalt_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Cobalt API error: {response.status_code}")
        
        cobalt_data = response.json()
        print(f"Cobalt response: {cobalt_data}")
        
        # Check response status
        status = cobalt_data.get("status")
        
        if status == "error":
            error_msg = cobalt_data.get("error", {}).get("code", "Unknown error")
            raise HTTPException(status_code=400, detail=f"Cobalt error: {error_msg}")
        
        if status not in ["tunnel", "redirect"]:
            raise HTTPException(status_code=400, detail=f"Unexpected Cobalt status: {status}")
        
        # Get the download URL
        download_url = cobalt_data.get("url")
        if not download_url:
            raise HTTPException(status_code=400, detail="No download URL from Cobalt")
        
        # Extract basic info (Cobalt doesn't provide all metadata, so we'll use defaults)
        filename = cobalt_data.get("filename", "video.mp4")
        
        # Determine platform from URL
        platform = "Unknown"
        if "youtube.com" in video_request.url or "youtu.be" in video_request.url:
            platform = "YouTube"
        elif "instagram.com" in video_request.url:
            platform = "Instagram"
        elif "tiktok.com" in video_request.url:
            platform = "TikTok"
        elif "facebook.com" in video_request.url or "fb.watch" in video_request.url:
            platform = "Facebook"
        elif "twitter.com" in video_request.url or "x.com" in video_request.url:
            platform = "Twitter"
        
        # Create response with single format (Cobalt provides best quality)
        base_url = str(request.base_url).rstrip('/')
        
        formats = [
            {
                "label": "Best Quality",
                "quality": "hd",
                "file_size": None,  # Cobalt doesn't provide size info
                "url": download_url,
                "ext": "mp4"
            },
            {
                "label": "Audio Only",
                "quality": "audio",
                "file_size": None,
                "url": f"{base_url}/api/cobalt-audio?url={video_request.url}",
                "ext": "mp3"
            }
        ]
        
        video_data = {
            "title": filename.replace(".mp4", "").replace(".webm", ""),
            "thumbnail": None,  # Cobalt doesn't provide thumbnails
            "platform": platform,
            "duration": None,  # Cobalt doesn't provide duration
            "formats": formats
        }
        
        return video_data
        
    except requests.exceptions.RequestException as e:
        print(f"Network error calling Cobalt API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        print(f"Error processing URL: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

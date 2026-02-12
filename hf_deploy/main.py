from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import requests
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
    print("🚀 STARTUP: SHEROV BACKEND V6 (Invidious + Cobalt + yt-dlp)")
    print(f"📦 yt-dlp version: {yt_dlp.version.__version__}")
    print("✅ YouTube: Invidious (cookie-free!)")
    print("✅ Others: Cobalt → yt-dlp fallback")
    print("--------------------------------------------------")
    import patch_dns
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
    """Extract video info using platform-specific extractors."""
    
    # Clean URL (remove tracking parameters)
    clean_url = video_request.url
    if '?si=' in clean_url or '&si=' in clean_url:
        clean_url = clean_url.split('?si=')[0].split('&si=')[0]
    
    print(f"Processing URL: {video_request.url}")
    print(f"Cleaned URL: {clean_url}")
    
    # Check if it's YouTube
    is_youtube = "youtube.com" in clean_url or "youtu.be" in clean_url
    
    if is_youtube:
        # Try Invidious for YouTube (cookie-free!)
        try:
            print("Attempting Invidious API extraction (YouTube)...")
            return await extract_with_invidious(clean_url, request)
        except Exception as inv_error:
            print(f"Invidious failed: {str(inv_error)}, falling back to yt-dlp...")
            # Fallback to yt-dlp for YouTube
            try:
                return await extract_with_ytdlp(video_request.url, request)
            except Exception as ytdlp_error:
                print(f"yt-dlp also failed: {str(ytdlp_error)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"YouTube extraction failed. Invidious: {str(inv_error)}, yt-dlp: {str(ytdlp_error)}"
                )
    else:
        # Try Cobalt for other platforms
        try:
            print("Attempting Cobalt API extraction...")
            return await extract_with_cobalt(clean_url, request)
        except HTTPException as e:
            if e.status_code == 400:
                print(f"Cobalt failed with 400, falling back to yt-dlp...")
                try:
                    return await extract_with_ytdlp(video_request.url, request)
                except Exception as ytdlp_error:
                    print(f"yt-dlp also failed: {str(ytdlp_error)}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Both Cobalt and yt-dlp failed. Cobalt: {e.detail}, yt-dlp: {str(ytdlp_error)}"
                    )
            raise

async def extract_with_invidious(url: str, request: Request):
    """Extract video info using Invidious API (YouTube only, cookie-free)."""
    import re
    
    # Extract video ID from URL
    video_id = None
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "youtube.com/watch?v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    
    if not video_id:
        raise ValueError("Could not extract YouTube video ID")
    
    print(f"Extracted video ID: {video_id}")
    
    # Try multiple Invidious instances for reliability
    instances = [
        "https://invidious.io.lol",
        "https://inv.nadeko.net",
        "https://invidious.nerdvpn.de"
    ]
    
    last_error = None
    for instance in instances:
        try:
            invidious_url = f"{instance}/api/v1/videos/{video_id}"
            print(f"Trying Invidious instance: {instance}")
            
            response = requests.get(invidious_url, timeout=10)
            
            if response.status_code != 200:
                last_error = f"{instance} returned {response.status_code}"
                continue
            
            data = response.json()
            
            # Get adaptive formats (best quality)
            formats_list = []
            base_url = str(request.base_url).rstrip('/')
            
            # Add video formats
            if 'adaptiveFormats' in data:
                for fmt in data['adaptiveFormats']:
                    if fmt.get('type', '').startswith('video'):
                        quality_label = fmt.get('qualityLabel', 'Unknown')
                        formats_list.append({
                            "label": f"{quality_label} (Invidious)",
                            "quality": "hd" if "1080" in quality_label or "720" in quality_label else "sd",
                            "file_size": fmt.get('size'),
                            "url": fmt.get('url'),
                            "ext": "mp4"
                        })
            
            # Add audio format
            for fmt in data.get('adaptiveFormats', []):
                if fmt.get('type', '').startswith('audio'):
                    formats_list.append({
                        "label": "Audio Only",
                        "quality": "audio",
                        "file_size": fmt.get('size'),
                        "url": fmt.get('url'),
                        "ext": "mp3"
                    })
                    break
            
            if not formats_list:
                last_error = f"{instance} returned no formats"
                continue
            
            return {
                "title": data.get('title', 'Unknown'),
                "thumbnail": data.get('videoThumbnails', [{}])[0].get('url') if data.get('videoThumbnails') else None,
                "platform": "YouTube",
                "duration": str(data.get('lengthSeconds', 0)) + "s",
                "formats": formats_list[:5]  # Limit to top 5 formats
            }
            
        except Exception as e:
            last_error = f"{instance}: {str(e)}"
            continue
    
    # All instances failed
    raise HTTPException(status_code=400, detail=f"All Invidious instances failed. Last error: {last_error}")

async def extract_with_cobalt(url: str, request: Request):
    """Extract video info using Cobalt API."""
    import requests
    
    cobalt_url = "https://api.cobalt.tools/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "videoQuality": "max",
        "audioFormat": "mp3",
        "filenameStyle": "basic"
    }
    
    response = requests.post(cobalt_url, json=payload, headers=headers, timeout=15)
    
    if response.status_code != 200:
        try:
            error_data = response.json()
            error_detail = error_data.get("error", {}).get("code", response.text)
        except:
            error_detail = response.text
        raise HTTPException(status_code=400, detail=f"Cobalt: {error_detail}")
    
    cobalt_data = response.json()
    print(f"Cobalt response: {cobalt_data}")
    
    status = cobalt_data.get("status")
    
    if status == "error":
        error_msg = cobalt_data.get("error", {}).get("code", "Unknown error")
        raise HTTPException(status_code=400, detail=f"Cobalt: {error_msg}")
    
    if status not in ["tunnel", "redirect"]:
        raise HTTPException(status_code=400, detail=f"Cobalt: Unexpected status {status}")
    
    download_url = cobalt_data.get("url")
    if not download_url:
        raise HTTPException(status_code=400, detail="Cobalt: No download URL")
    
    filename = cobalt_data.get("filename", "video.mp4")
    
    # Determine platform
    platform = "Unknown"
    if "youtube.com" in url or "youtu.be" in url:
        platform = "YouTube"
    elif "instagram.com" in url:
        platform = "Instagram"
    elif "tiktok.com" in url:
        platform = "TikTok"
    elif "facebook.com" in url or "fb.watch" in url:
        platform = "Facebook"
    elif "twitter.com" in url or "x.com" in url:
        platform = "Twitter"
    
    base_url = str(request.base_url).rstrip('/')
    
    formats = [
        {
            "label": "Best Quality (Cobalt)",
            "quality": "hd",
            "file_size": None,
            "url": download_url,
            "ext": "mp4"
        },
        {
            "label": "Audio Only",
            "quality": "audio",
            "file_size": None,
            "url": f"{base_url}/api/cobalt-audio?url={url}",
            "ext": "mp3"
        }
    ]
    
    return {
        "title": filename.replace(".mp4", "").replace(".webm", ""),
        "thumbnail": None,
        "platform": platform,
        "duration": None,
        "formats": formats
    }

async def extract_with_ytdlp(url: str, request: Request):
    """Extract video info using yt-dlp (fallback)."""
    import os
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'socket_timeout': 30,
        'force_ipv4': True,
    }
    
    # Add cookies if file exists
    cookie_path = '/home/user/app/cookies.txt'
    if os.path.exists(cookie_path):
        ydl_opts['cookiefile'] = cookie_path
        print(f"Using cookies from {cookie_path}")
    else:
        print("WARNING: No cookies.txt found. YouTube may require authentication.")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if not info:
            raise ValueError("Could not extract video info")
        
        base_url = str(request.base_url).rstrip('/')
        
        # Simple format extraction
        formats = [
            {
                "label": "Best Quality (yt-dlp)",
                "quality": "hd",
                "file_size": None,
                "url": f"{base_url}/api/stream?url={url}&type=video",
                "ext": "mp4"
            },
            {
                "label": "Audio Only",
                "quality": "audio",
                "file_size": None,
                "url": f"{base_url}/api/stream?url={url}&type=audio",
                "ext": "mp3"
            }
        ]
        
        return {
            "title": info.get('title', 'Unknown'),
            "thumbnail": info.get('thumbnail'),
            "platform": info.get('extractor_key', 'Unknown'),
            "duration": info.get('duration_string'),
            "formats": formats
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

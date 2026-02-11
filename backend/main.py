from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import uvicorn
import subprocess
import shlex

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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
    
    # Assuming standard venv structure: python is in Scripts/python.exe, yt-dlp is in Scripts/yt-dlp.exe
    yt_dlp_path = os.path.join(os.path.dirname(sys.executable), "yt-dlp.exe")
    if not os.path.exists(yt_dlp_path):
        # Fallback for non-Windows or different venv structure, though user is on Windows
        yt_dlp_path = "yt-dlp"

    # Build yt-dlp command to stream to stdout
    cmd = [yt_dlp_path, url, "-o", "-", "--quiet", "--no-warnings"]
    
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

@app.post("/api/download")
async def extract_video_info(request_body: VideoRequest, request: FastAPI.Request = None):
    # Note: We need the raw Request object to get the base URL
    # But since we use Pydantic model for body, we can access Request via dependency injection if we import Request from fastapi
    from fastapi import Request
    
    # We need to change the function signature to accept Request
    pass

# Redefining the function with correct signature and logic
@app.post("/api/download")
async def extract_video_info(video_request: VideoRequest, request: Request):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'socket_timeout': 10,
    }

    try:
        print(f"Processing URL: {video_request.url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_request.url, download=False)
            
            if not info:
                raise ValueError("Could not extract video info")

            formats = []
            seen_qualities = set() # Track by quality label (e.g. "1080p") to avoid duplicates

            # Get base URL from the incoming request (e.g. https://my-app.onrender.com)
            base_url = str(request.base_url).rstrip('/')

            # Helper to format bytes
            def format_size(bytes_val):
                if not bytes_val:
                    return None
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if bytes_val < 1024.0:
                        return f"{bytes_val:.1f} {unit}"
                    bytes_val /= 1024.0
                return f"{bytes_val:.1f} TB"

            # Helper to calculate size from bitrate if missing
            def get_size(f_info, duration_s):
                size = f_info.get('filesize') or f_info.get('filesize_approx')
                if size:
                    return size
                
                # Fallback: Calculate from bitrate (tbr)
                tbr = f_info.get('tbr')
                if tbr and duration_s:
                    # tbr is in kbit/s. duration in seconds.
                    # size = (tbr * 1024 * duration) / 8 bytes
                    return (tbr * 1024 * duration_s) / 8
                return 0

            duration_s = info.get('duration') or 0

            # 1. Find best Audio
            best_audio = None
            raw_formats = info.get('formats', [])
            for f in raw_formats:
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    if not best_audio or f.get('tbr', 0) > best_audio.get('tbr', 0):
                        best_audio = f
            
            audio_size = 0
            if best_audio:
                audio_size = get_size(best_audio, duration_s)
                formats.append({
                    "label": "Audio (Best)",
                    "quality": "audio",
                    "file_size": format_size(audio_size),
                    "url": f"{base_url}/api/stream?url={video_request.url}&type=audio",
                    "ext": "mp3"
                })

            # 2. Analyze available video heights from raw formats
            # We want to offer 360p, 480p, 720p, 1080p, etc. if they exist in SOME form (video-only or merged)
            available_heights = {} # Map height -> best format dict for that height
            
            for f in raw_formats:
                h = f.get('height')
                if not h: continue
                
                # Keep the format with the best bitrate/filesize for this height
                current_best = available_heights.get(h)
                f_size = get_size(f, duration_s)
                c_size = get_size(current_best, duration_s) if current_best else 0
                
                if not current_best or f_size > c_size:
                    available_heights[h] = f
            
            # Sort heights descending
            sorted_heights = sorted(list(available_heights.keys()), reverse=True)

            for h in sorted_heights:
                if h < 360: continue # Skip qualities lower than 360p as requested

                f = available_heights[h]
                video_size = get_size(f, duration_s)
                
                # If video has no audio (vcodec!=none, acodec=none), add best_audio size to estimate
                total_size = video_size
                if f.get('acodec') == 'none':
                     total_size += audio_size

                label = f"{h}p"
                quality_type = "sd"
                if h >= 2160:
                    quality_type = "4k"
                    label += " 4K"
                elif h >= 1440:
                    quality_type = "2k"
                    label += " 2K"
                elif h >= 1080:
                    quality_type = "hd"
                    label += " Full HD"
                elif h >= 720:
                    quality_type = "hd"
                    label += " HD"
                else:
                     label += " SD"

                if label in seen_qualities:
                    continue

                # Use proxy stream for guaranteed quality + audio
                formats.append({
                    "label": label,
                    "quality": quality_type,
                    "file_size": format_size(total_size),
                    "url": f"{base_url}/api/stream?url={video_request.url}&quality={h}&type=video",
                    "ext": "mp4"
                })
                seen_qualities.add(label)

            # Extract relevant info
            video_data = {
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "platform": info.get('extractor_key'),
                "duration": info.get('duration_string'),
                "formats": formats
            }
            return video_data
    except Exception as e:
        print(f"Error processing URL: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

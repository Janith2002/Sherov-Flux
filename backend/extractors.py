"""
Video Extractors - Multi-strategy extraction system
Uses FREE services: Cobalt API (no API key) + yt-dlp fallback
"""

import httpx
import yt_dlp
import random
from typing import Dict, Optional, List
from abc import ABC, abstractmethod
import config

class BaseExtractor(ABC):
    """Base class for all extractors"""
    
    @abstractmethod
    async def extract(self, url: str) -> Optional[Dict]:
        """Extract video info from URL"""
        pass
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(config.USER_AGENTS)


class CobaltExtractor(BaseExtractor):
    """
    Cobalt API Extractor - FREE, no API key needed
    Best for: TikTok, Instagram, Twitter, Reddit
    """
    
    def __init__(self):
        self.api_urls = [config.COBALT_API_URL] + config.COBALT_FALLBACK_URLS
    
    async def extract(self, url: str) -> Optional[Dict]:
        """Extract using Cobalt API"""
        
        payload = {
            "url": url,
            "vCodec": "h264",
            "vQuality": "max",
            "aFormat": "mp3",
            "filenamePattern": "basic",
            "isAudioOnly": False,
            "disableMetadata": False
        }
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.get_random_user_agent()
        }
        
        # Try each Cobalt instance
        for api_url in self.api_urls:
            try:
                async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
                    response = await client.post(api_url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return self._parse_cobalt_response(data, url)
                    
            except Exception as e:
                print(f"Cobalt API ({api_url}) failed: {str(e)}")
                continue
        
        return None
    
    def _parse_cobalt_response(self, data: Dict, original_url: str) -> Optional[Dict]:
        """Parse Cobalt API response to standard format"""
        
        if data.get("status") != "success" and data.get("status") != "stream":
            return None
        
        formats = []
        
        # Video URL
        video_url = data.get("url")
        if video_url:
            formats.append({
                "label": "Best Quality",
                "quality": "hd",
                "file_size": None,
                "url": video_url,
                "ext": "mp4"
            })
        
        # Audio URL
        audio_url = data.get("audio")
        if audio_url:
            formats.append({
                "label": "Audio (Best)",
                "quality": "audio",
                "file_size": None,
                "url": audio_url,
                "ext": "mp3"
            })
        
        # Picker (multiple quality options)
        picker = data.get("picker")
        if picker and isinstance(picker, list):
            for idx, item in enumerate(picker):
                formats.append({
                    "label": f"Quality {idx + 1}",
                    "quality": "hd" if idx == 0 else "sd",
                    "file_size": None,
                    "url": item.get("url"),
                    "ext": "mp4"
                })
        
        return {
            "title": data.get("filename", "Video"),
            "thumbnail": None,
            "platform": "Cobalt",
            "duration": None,
            "formats": formats
        }


class YtDlpExtractor(BaseExtractor):
    """
    Enhanced yt-dlp Extractor
    Best for: YouTube, Facebook
    """
    
    async def extract(self, url: str) -> Optional[Dict]:
        """Extract using yt-dlp"""
        
        ydl_opts = config.YT_DLP_OPTIONS.copy()
        ydl_opts['user_agent'] = self.get_random_user_agent()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return None
                
                return self._parse_ytdlp_response(info)
                
        except Exception as e:
            print(f"yt-dlp extraction failed: {str(e)}")
            return None
    
    def _parse_ytdlp_response(self, info: Dict) -> Dict:
        """Parse yt-dlp response to standard format"""
        
        formats = []
        seen_qualities = set()
        
        duration_s = info.get('duration') or 0
        
        # Helper functions
        def format_size(bytes_val):
            if not bytes_val:
                return None
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_val < 1024.0:
                    return f"{bytes_val:.1f} {unit}"
                bytes_val /= 1024.0
            return f"{bytes_val:.1f} TB"
        
        def get_size(f_info, duration_s):
            size = f_info.get('filesize') or f_info.get('filesize_approx')
            if size:
                return size
            tbr = f_info.get('tbr')
            if tbr and duration_s:
                return (tbr * 1024 * duration_s) / 8
            return 0
        
        # Best Audio
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
                "url": best_audio.get('url'),
                "ext": "mp3"
            })
        
        # Video qualities
        available_heights = {}
        for f in raw_formats:
            h = f.get('height')
            if not h:
                continue
            
            current_best = available_heights.get(h)
            f_size = get_size(f, duration_s)
            c_size = get_size(current_best, duration_s) if current_best else 0
            
            if not current_best or f_size > c_size:
                available_heights[h] = f
        
        sorted_heights = sorted(list(available_heights.keys()), reverse=True)
        
        for h in sorted_heights:
            if h < 360:
                continue
            
            f = available_heights[h]
            video_size = get_size(f, duration_s)
            total_size = video_size + (audio_size if f.get('acodec') == 'none' else 0)
            
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
            
            formats.append({
                "label": label,
                "quality": quality_type,
                "file_size": format_size(total_size),
                "url": f.get('url'),
                "ext": "mp4"
            })
            seen_qualities.add(label)
        
        return {
            "title": info.get('title'),
            "thumbnail": info.get('thumbnail'),
            "platform": info.get('extractor_key'),
            "duration": info.get('duration_string'),
            "formats": formats
        }


class VideoExtractorManager:
    """
    Manages extraction strategies with automatic fallback
    Strategy: Cobalt first (fast, free), then yt-dlp
    """
    
    def __init__(self):
        self.cobalt = CobaltExtractor()
        self.ytdlp = YtDlpExtractor()
    
    def detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        url_lower = url.lower()
        for platform, patterns in config.PLATFORM_PATTERNS.items():
            if any(pattern in url_lower for pattern in patterns):
                return platform
        return 'unknown'
    
    async def extract(self, url: str) -> Dict:
        """
        Extract video info with automatic fallback
        
        Strategy:
        1. For TikTok/Instagram/Twitter/Reddit: Try Cobalt first
        2. For YouTube/Facebook: Try yt-dlp first
        3. Always fallback to the other method if primary fails
        """
        
        platform = self.detect_platform(url)
        print(f"Detected platform: {platform}")
        
        # Determine primary strategy
        if platform in ['tiktok', 'instagram', 'twitter', 'reddit']:
            primary = self.cobalt
            fallback = self.ytdlp
            primary_name = "Cobalt"
            fallback_name = "yt-dlp"
        else:
            primary = self.ytdlp
            fallback = self.cobalt
            primary_name = "yt-dlp"
            fallback_name = "Cobalt"
        
        # Try primary strategy
        print(f"Trying {primary_name}...")
        result = await primary.extract(url)
        
        if result and result.get('formats'):
            print(f"✓ {primary_name} succeeded")
            return result
        
        # Fallback strategy
        print(f"✗ {primary_name} failed, trying {fallback_name}...")
        result = await fallback.extract(url)
        
        if result and result.get('formats'):
            print(f"✓ {fallback_name} succeeded")
            return result
        
        # Both failed
        raise Exception(f"All extraction methods failed for {platform}")

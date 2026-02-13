"""
Configuration for Video Downloader Backend
Optimized for free hosting platforms (Hugging Face Spaces, Render, Railway)
"""

# Cobalt API - FREE, no API key needed
COBALT_API_URL = "https://api.cobalt.tools/api/json"

# Alternative Cobalt instances (fallbacks)
COBALT_FALLBACK_URLS = [
    "https://co.wuk.sh/api/json",
    "https://cobalt-api.kwiatekmiki.com/api/json"
]

# Cache settings
CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 100

# Request settings
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# User agents for rotation (mimic real browsers)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Platform detection
PLATFORM_PATTERNS = {
    'tiktok': ['tiktok.com', 'vm.tiktok.com'],
    'youtube': ['youtube.com', 'youtu.be'],
    'instagram': ['instagram.com', 'instagr.am'],
    'facebook': ['facebook.com', 'fb.watch', 'fb.com'],
    'twitter': ['twitter.com', 'x.com'],
    'reddit': ['reddit.com', 'redd.it']
}

# yt-dlp configuration
YT_DLP_OPTIONS = {
    'quiet': False,
    'verbose': True,
    'no_warnings': False,
    'format': 'best',
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'no_color': True,
    'socket_timeout': 30,
    'force_ipv4': True,
    'source_address': '0.0.0.0',
    'extractor_retries': 3,
    'fragment_retries': 3,
    'skip_unavailable_fragments': True,
}

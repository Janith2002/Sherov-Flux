# 🚀 Free Backend Hosting Guide

## Best FREE Platforms for Video Downloader Backend

### 1. **Hugging Face Spaces** (RECOMMENDED)
- ✅ **FREE Forever**
- ✅ **No Credit Card Required**
- ✅ **Persistent Storage**
- ✅ **Auto-deployment from Git**
- ⚠️ May have network restrictions (solved with Cobalt API)

**Deploy Steps:**
```bash
# 1. Create account at https://huggingface.co
# 2. Create new Space (Docker type)
# 3. Copy files from hf_deploy/ folder
# 4. Push to Space repository
```

### 2. **Render.com**
- ✅ **FREE Tier Available**
- ✅ **Auto-deploy from GitHub**
- ✅ **Better network access**
- ⚠️ Sleeps after 15 min inactivity (wakes up in ~30s)

**Deploy Steps:**
```bash
# 1. Create account at https://render.com
# 2. Connect GitHub repository
# 3. Select "Web Service"
# 4. Build command: pip install -r requirements.txt
# 5. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3. **Railway.app**
- ✅ **$5 FREE Credit/month**
- ✅ **Fast deployment**
- ✅ **Good for testing**
- ⚠️ Credit runs out quickly with heavy usage

### 4. **Fly.io**
- ✅ **FREE Tier**
- ✅ **Global edge network**
- ⚠️ Requires credit card for verification

---

## Deployment Files

### For Hugging Face Spaces

Create these files in `hf_deploy/` folder:

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY extractors.py .
COPY config.py .
COPY patch_dns.py .

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

#### `README.md`
```markdown
---
title: Sherov Flux Backend
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Sherov Flux Video Downloader Backend

Multi-platform video downloader supporting YouTube, TikTok, Instagram, Facebook, Twitter, and Reddit.

**Features:**
- 🚀 Cobalt API integration (fast, no watermark)
- 🔄 Automatic fallback to yt-dlp
- 💾 Smart caching (5-minute TTL)
- 🌐 CORS enabled for all origins

**API Endpoint:** `/api/download`
```

### For Render.com

Create `render.yaml`:
```yaml
services:
  - type: web
    name: sherov-flux-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

---

## Environment Variables (Optional)

No API keys needed! The Cobalt API is completely free.

---

## Testing Locally

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run the server
python main.py

# 3. Test with curl
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@test/video/123"}'
```

---

## Update Frontend

Update your frontend `.env` file:

```env
# For Hugging Face Spaces
VITE_API_URL=https://YOUR-USERNAME-sherov-flux.hf.space

# For Render
VITE_API_URL=https://sherov-flux-backend.onrender.com

# For Railway
VITE_API_URL=https://sherov-flux-backend.up.railway.app
```

---

## Troubleshooting

### Issue: "All extraction methods failed"
**Solution:** The video might be private, deleted, or age-restricted. Try a different URL.

### Issue: "Cobalt API unavailable"
**Solution:** The system automatically falls back to yt-dlp. Check `/api/health` endpoint.

### Issue: Slow response on Render
**Solution:** Free tier sleeps after inactivity. First request takes ~30s to wake up.

### Issue: YouTube videos fail
**Solution:** This is expected on some cloud platforms. The Cobalt API doesn't support YouTube well, but yt-dlp should work for most videos.

---

## Platform Comparison

| Platform | Speed | Reliability | Network | Sleep | Best For |
|----------|-------|-------------|---------|-------|----------|
| **Hugging Face** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Never | Production |
| **Render** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 15min | Best overall |
| **Railway** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Never | Testing |
| **Fly.io** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Never | Advanced |

**Recommendation:** Start with **Render.com** for best performance, or **Hugging Face** if you don't want sleep issues.

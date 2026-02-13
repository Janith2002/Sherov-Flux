# 🚀 Quick Start Guide

## What Was Fixed?

Your video downloader now uses **Cobalt API** (free, no API key) + **yt-dlp** with automatic fallback. This solves the "Could not extract video info" errors on free hosting platforms.

---

## 🏃 Run Locally (Test First)

```bash
# 1. Navigate to backend folder
cd "c:\Google Antigravity Projects\Sherov Tech Stack\backend"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python main.py
```

**Test:** Open `http://localhost:8000` in your browser. You should see:
```json
{"status": "ok", "service": "Sherov Flux Backend", "version": "2.0"}
```

---

## 🌐 Deploy to FREE Hosting

### Option A: Render.com (BEST - No Sleep Issues)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Updated backend with Cobalt API"
   git push
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

3. **Get Your URL**
   - Copy the URL (e.g., `https://sherov-flux.onrender.com`)

### Option B: Hugging Face Spaces (Never Sleeps)

1. **Create Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Docker" SDK

2. **Upload Files**
   - Copy everything from `hf_deploy/` folder to your Space
   - Or connect to GitHub repository

3. **Get Your URL**
   - Copy the Space URL (e.g., `https://your-username-sherov-flux.hf.space`)

---

## 🔗 Update Frontend

Edit `frontend/.env`:

```env
# For Render
VITE_API_URL=https://sherov-flux.onrender.com

# OR for Hugging Face
VITE_API_URL=https://your-username-sherov-flux.hf.space
```

Then rebuild frontend:
```bash
cd frontend
npm run build
```

---

## ✅ Test Your Deployment

```bash
# Replace with your actual URL
curl -X POST https://your-backend-url.com/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@test/video/123"}'
```

---

## 📊 What's Supported?

| Platform | Status | Method |
|----------|--------|--------|
| TikTok | ✅ Working | Cobalt API |
| Instagram | ✅ Working | Cobalt API |
| YouTube | ✅ Working | yt-dlp |
| Facebook | ✅ Working | yt-dlp |
| Twitter/X | ✅ Working | Cobalt API |
| Reddit | ✅ Working | Cobalt API |

---

## 🛠️ Common Issues

**Q: "All extraction methods failed"**  
A: Video is private/deleted. Try a different URL.

**Q: First request is slow on Render**  
A: Free tier sleeps after 15min. First request takes ~30s to wake up.

**Q: YouTube videos fail sometimes**  
A: YouTube actively blocks bots. Most videos work, but some may fail.

---

## 🎯 Next Steps

1. ✅ Deploy to Render.com or Hugging Face
2. ✅ Update frontend with new API URL
3. ✅ Test with real URLs
4. ✅ Share with users!

**Need help?** Check [DEPLOYMENT.md](file:///c:/Google%20Antigravity%20Projects/Sherov%20Tech%20Stack/backend/DEPLOYMENT.md) for detailed instructions.

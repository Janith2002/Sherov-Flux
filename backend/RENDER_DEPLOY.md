# 🚀 Render.com Deployment Guide

## Quick Deploy Steps

### 1. Push Code to GitHub

```bash
# Navigate to project root
cd "c:\Google Antigravity Projects\Sherov Tech Stack"

# Add all changes
git add .

# Commit
git commit -m "Add Cobalt API backend with auto-fallback"

# Push to GitHub
git push origin main
```

### 2. Deploy on Render.com

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Sign in with GitHub

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository: `Janith2002/Sherov-Flux`

3. **Configure Service**
   - **Name:** `sherov-flux-backend`
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

4. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment

### 3. Get Your Backend URL

After deployment completes, you'll get a URL like:
```
https://sherov-flux-backend.onrender.com
```

### 4. Update Frontend

Edit `frontend/.env`:
```env
VITE_API_URL=https://sherov-flux-backend.onrender.com
```

Then rebuild frontend:
```bash
cd frontend
npm run build
```

### 5. Test Your Deployment

```bash
# Test health endpoint
curl https://sherov-flux-backend.onrender.com/

# Test download (replace with your actual URL)
curl -X POST https://sherov-flux-backend.onrender.com/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- 750 hours/month free (enough for most use cases)

✅ **Advantages:**
- Best network access (no YouTube blocking)
- Auto-deploy on git push
- Free SSL certificate
- Easy to use

---

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is in the `backend/` folder
- Verify Python version is 3.11 or higher

### Service Won't Start
- Check logs in Render dashboard
- Verify start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Slow First Request
- This is normal - free tier sleeps after 15min
- Consider upgrading to paid plan ($7/month) for always-on service

---

## Alternative: Render Blueprint (Easier)

If you have `render.yaml` in your backend folder, Render can auto-configure:

1. Go to: https://dashboard.render.com/blueprints
2. Click "New Blueprint Instance"
3. Connect repository
4. Select `backend/render.yaml`
5. Click "Apply"

Done! ✅

# 🚀 Update Netlify Deployment

Your backend is live at `https://sherov-flux.onrender.com`. now we need to point your Netlify frontend to it.

## Option 1: Update via Netlify Dashboard (Easiest)

1. Go to **[Netlify Dashboard](https://app.netlify.com)**
2. Click on your site: **`sherov-flux`**
3. Go to **Site settings** > **Environment variables**
4. Check if `VITE_API_URL` exists
   - **If yes:** Edit it to `https://sherov-flux.onrender.com`
   - **If no:** Add new variable:
     - Key: `VITE_API_URL`
     - Value: `https://sherov-flux.onrender.com`
5. Go to **Deploys** tab and click **"Trigger deploy"** > **"Deploy site"**

## Option 2: Deploy from CLI (If you have Netlify CLI)

```bash
# 1. Build the frontend with the new env var
cd "c:\Google Antigravity Projects\Sherov Tech Stack\frontend"
npm run build

# 2. Deploy to Netlify (if you have the CLI installed)
npm install -g netlify-cli
netlify login
netlify link
netlify deploy --prod --dir=dist
```

## Option 3: Push to GitHub (If Netlify is connected to GitHub)

Since we already updated `frontend/.env`, you can just push the changes:

```bash
# In your project root
git add frontend/.env
git commit -m "Update frontend to use live Render backend"
git push origin main
```

**Netlify will detect the push and auto-redeploy!**

---

### ❓ Which method are you using?

- **GitHub Connected?** -> Use Option 3 (Recommended)
- **Manual Upload?** -> Run `npm run build` and upload the `dist` folder

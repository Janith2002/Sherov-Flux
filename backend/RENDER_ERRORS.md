# 🔧 Common Render Deployment Errors & Fixes

## Error 1: "Could not find a version that satisfies the requirement yt-dlp @ git+..."

**Problem:** Render can't install yt-dlp from git

**Fix:** Use stable PyPI version instead

**Solution:**
```bash
# Update requirements.txt
yt-dlp>=2024.1.0  # Instead of git+https://...
```

---

## Error 2: "ModuleNotFoundError: No module named 'extractors'"

**Problem:** Python can't find the extractors.py file

**Fix:** Ensure Root Directory is set correctly

**Solution:**
- Root Directory should be: `backend`
- OR update imports to use absolute paths

---

## Error 3: "ERROR: Could not build wheels for..."

**Problem:** Missing system dependencies

**Fix:** Add build dependencies

**Solution:**
Add to requirements.txt:
```
uvicorn[standard]>=0.24.0  # Instead of just uvicorn
```

---

## Error 4: "Application startup failed"

**Problem:** Port binding or import errors

**Fix:** Check Start Command

**Solution:**
Start Command should be:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Error 5: "No module named 'patch_dns'"

**Problem:** Missing patch_dns.py file

**Fix:** Make sure patch_dns.py is in backend folder

**Solution:**
The file should be committed to git. Check with:
```bash
git ls-files backend/patch_dns.py
```

---

## Quick Fix: Updated Requirements

I've created an updated `requirements.txt` that should work better on Render:

**Key Changes:**
- ✅ Use stable yt-dlp from PyPI (not git)
- ✅ Add `uvicorn[standard]` for better compatibility
- ✅ Add `python-multipart` for form handling

---

## Next Steps:

1. **Commit the fixed requirements.txt:**
   ```bash
   git add backend/requirements.txt
   git commit -m "Fix requirements for Render deployment"
   git push origin main
   ```

2. **Trigger redeploy on Render:**
   - Go to your service dashboard
   - Click "Manual Deploy" → "Deploy latest commit"
   - OR it will auto-deploy when you push

3. **Watch the logs** for any new errors

---

## Still Getting Errors?

**Please share the exact error message** from the Render logs, and I'll provide a specific fix!

Common log locations:
- Build logs: Shows dependency installation
- Deploy logs: Shows server startup
- Runtime logs: Shows application errors

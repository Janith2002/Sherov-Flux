# ⚡ Sherov Flux

A **Python backend service** with a REST API — built for deployment on Render with full Docker support and DNS patching for production environments.

## ✨ Features

- 🚀 Python FastAPI/Flask backend
- 🐳 Docker containerized
- ☁️ Render deployment ready (`render.yaml`)
- 🔧 DNS patch for production networking
- 📦 Clean modular architecture

## 🛠️ Tech Stack

- **Language:** Python 3
- **Framework:** FastAPI / Flask
- **Deployment:** Render, Docker
- **Config:** `render.yaml`, `runtime.txt`

## 📁 Project Structure

```
backend/
├── main.py           # App entry point
├── config.py         # Configuration
├── extractors.py     # Core extraction logic
├── patch_dns.py      # DNS patching for production
├── Dockerfile        # Container setup
├── render.yaml       # Render deployment config
└── requirements.txt  # Dependencies
```

## 🚀 Getting Started

```bash
git clone https://github.com/Janith2002/Sherov-Flux.git
cd Sherov-Flux/backend

pip install -r requirements.txt
python main.py
```

### Deploy to Render

1. Connect this repo to [Render](https://render.com)
2. Render auto-detects `render.yaml`
3. Deploy 🚀

---

> Built by [Janith Akalanka](https://github.com/Janith2002)

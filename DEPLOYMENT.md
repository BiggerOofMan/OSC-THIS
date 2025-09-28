# 🚀 Deployment Guide for THIS (The Hell Is This?)

This guide covers several production deployment options:

1. Docker (single container)
2. Ubuntu VM (systemd + gunicorn + nginx)
3. Managed PaaS (Render / Railway / Fly.io / Azure App Service)
4. Local network Raspberry Pi / mini PC

---
## 0. Production Considerations
| Concern | Action |
| ------- | ------ |
| Secrets | Use real environment variables, never commit .env with keys |
| HTTPS | Terminate TLS at a reverse proxy (nginx / cloud) |
| Logging | Stream stdout/err, rotate if writing to file |
| Resource Usage | Tesseract + OpenCV: ensure at least 1GB RAM (2GB recommended) |
| LLM Failures | Gracefully degrade (already implemented) |
| Translation | googletrans may fail intermittently; degrade is OK |
| File Storage | results/ can grow; rotate or disable SAVE_RESULTS |

---
## 1. Deploy with Docker (Fastest)
### Build
```bash
docker build -t this-app:latest .
```
### Run
```bash
docker run -d --name this-app \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e OPENAI_BASE_URL=https://api.ai.it.ufl.edu \
  -e LLM_MODEL_NAME=llama-3.3-70b-instruct \
  -e SAVE_RESULTS=True \
  -v $(pwd)/results:/app/results \
  this-app:latest
```
Visit: http://localhost:8000

(Optional) Use an .env file:
```bash
docker run --env-file .env -p 8000:8000 this-app:latest
```

---
## 2. Ubuntu VM Deployment (Gunicorn + Nginx)
### Install system packages
```bash
sudo apt update && sudo apt install -y python3-venv python3-dev build-essential \
  tesseract-ocr tesseract-ocr-eng libgl1 libglib2.0-0 nginx
```
### App user & directory
```bash
sudo useradd -r -m -d /opt/thisapp this
sudo mkdir -p /opt/thisapp
sudo chown -R $USER:this /opt/thisapp
```
### Clone / Copy code & setup venv
```bash
cd /opt/thisapp
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
### Test run
```bash
gunicorn wsgi:app -b 0.0.0.0:8000 -w 2 --threads 4
```
### systemd service
Create `/etc/systemd/system/this.service`:
```
[Unit]
Description=THIS Ingredient Analyzer
After=network.target

[Service]
User=this
Group=this
WorkingDirectory=/opt/thisapp
Environment="OPENAI_API_KEY=your_key" "OPENAI_BASE_URL=https://api.ai.it.ufl.edu" "LLM_MODEL_NAME=llama-3.3-70b-instruct" "SAVE_RESULTS=True"
ExecStart=/opt/thisapp/venv/bin/gunicorn wsgi:app -c gunicorn.conf.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Enable & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now this
```
### Nginx reverse proxy
Create `/etc/nginx/sites-available/this`:
```
server {
  listen 80;
  server_name your_domain_or_ip;
  client_max_body_size 16M;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```
Enable:
```bash
sudo ln -s /etc/nginx/sites-available/this /etc/nginx/sites-enabled/this
sudo nginx -t && sudo systemctl reload nginx
```
### HTTPS (Let’s Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain
```

---
## 3. Render / Railway / Fly.io / Azure
### General settings
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn wsgi:app -c gunicorn.conf.py`
- Python version: 3.11
- Add env vars (OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL_NAME, SAVE_RESULTS)
- Persist `results/` only if needed (or disable with SAVE_RESULTS=False)

For Fly.io add a `fly.toml` (not included yet—ask if needed).

---
## 4. Raspberry Pi / ARM Notes
- Replace base image in Dockerfile with `python:3.11-bookworm` for better ARM support.
- Install `tesseract-ocr` and `tesseract-ocr-eng` via apt.
- Reduce workers: `workers=1` in `gunicorn.conf.py`.

---
## 5. Environment Variables Reference
| Var | Purpose | Default |
|-----|---------|---------|
| OPENAI_API_KEY | LLM auth | empty |
| OPENAI_BASE_URL | API endpoint | empty |
| LLM_MODEL_NAME | Model id | llama-3.3-70b-instruct |
| SAVE_RESULTS | Persist JSON analyses | True |
| LOG_LEVEL | Logging verbosity | INFO |
| MAX_CONTENT_LENGTH | Upload size limit | 16MB |

---
## 6. Operational Tasks
| Task | Command |
|------|---------|
| Tail logs (systemd) | `journalctl -u this -f` |
| Restart service | `sudo systemctl restart this` |
| Rebuild Docker | `docker build -t this-app:latest .` |
| Prune old results | `find results -type f -mtime +14 -delete` |

---
## 7. Hardening Ideas (Future)
- Add auth (basic token) to API endpoints
- Rate limiting with a proxy (nginx / traefik)
- Sentry or similar for error tracking
- Replace googletrans with a more reliable translation API

---
## 8. Troubleshooting
| Symptom | Fix |
|---------|-----|
| 401 on LLM | Verify key + model + endpoint; remove stale env overrides |
| OCR empty | Ensure tesseract installed + readable image | 
| App hangs | Reduce workers/threads; check memory |
| Large images fail | Increase `client_max_body_size` in nginx |

---
**Need another deployment target? Ask and I’ll generate the config.**

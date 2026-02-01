# Python AI Service Deployment

## Local Development

1. **Install Dependencies**
```bash
cd python-service
pip install -r requirements.txt
```

2. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. **Run Service**
```bash
python main.py
# Service runs on http://localhost:8000
```

## Docker Deployment

1. **Build Image**
```bash
docker build -t speecher-ai .
```

2. **Run Container**
```bash
docker run -d \
  --name speecher-ai \
  -p 8000:8000 \
  --env-file .env \
  speecher-ai
```

## VPS Deployment

1. **Server Requirements**
- Ubuntu 20.04+ or similar
- 4GB+ RAM (8GB recommended)
- 20GB+ storage
- GPU optional (CUDA support)

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

3. **Deploy Service**
```bash
# Clone repository
git clone <your-repo>
cd speecher/python-service

# Configure environment
cp .env.example .env
nano .env  # Add your credentials

# Build and run
docker build -t speecher-ai .
docker run -d \
  --name speecher-ai \
  -p 8000:8000 \
  --restart unless-stopped \
  --env-file .env \
  speecher-ai
```

4. **Setup Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Environment Variables

Required in `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SERVICE_SECRET=your_webhook_secret
```

## Health Check

Test service health:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "services": {
    "tts_engine": "ready",
    "job_processor": "ready", 
    "supabase": "connected"
  }
}
```

## Next.js Configuration

Add to `.env.local`:
```
PYTHON_SERVICE_URL=http://your-vps-ip:8000
PYTHON_SERVICE_SECRET=your_webhook_secret
```

## Storage Buckets

Create in Supabase dashboard:
- `audio-outputs` (private)
- `voice-models` (private)
- `user-assets` (private)
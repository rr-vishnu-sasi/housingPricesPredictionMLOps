# 🐳 Docker Deployment - Quick Start

## 🎯 What You Get

A **containerized ML API** with:
- 🚀 Flask API serving predictions
- ⚡ Redis cache (25x faster repeated predictions)
- 🔒 Production-ready (Gunicorn WSGI server)
- 📦 Portable (runs anywhere Docker runs)
- 🔧 Easy to deploy

---

## ⚡ Quick Start (3 Steps)

### 1. Start Everything

```bash
bash docker-run.sh
```

This will:
- ✅ Build Docker image
- ✅ Start Redis cache
- ✅ Start ML API
- ✅ Services ready in ~2 minutes

### 2. Test the API

```bash
# Health check
curl http://localhost:5000/health

# Make prediction
curl -X POST http://localhost:5000/predict \
  -H 'Content-Type: application/json' \
  -d '{"median_income":8.3,"housing_median_age":41,"total_rooms":880,"total_bedrooms":129,"population":322,"households":126,"latitude":37.88,"longitude":-122.23,"ocean_proximity":"NEAR BAY"}'
```

### 3. Stop When Done

```bash
docker-compose down
```

---

## 📊 What's Running

After `docker-run.sh`:

```
┌──────────────────────────────────┐
│  Docker Services                  │
├──────────────────────────────────┤
│  ✅ Redis Cache (port 6379)      │
│  ✅ ML API (port 5000)           │
└──────────────────────────────────┘
```

**Access:** http://localhost:5000

---

## 🎓 Simple Explanations

### What is Docker?

Think: **Portable lunch box** 🍱

- Everything packaged together
- Works on any table (computer)
- Nothing spills out
- Easy to share!

### What is Multi-Stage Build?

Think: **Cooking** 🍳

```
Stage 1 (Kitchen - LARGE):
├─ All cooking equipment
├─ All ingredients
├─ Prep and cook
└─ Make a mess!

Stage 2 (Serving Plate - SMALL):
├─ Just the finished dish
├─ Clean plate
└─ Ready to serve!

Result: Serve only what's needed!
```

### What is Docker Compose?

Think: **Restaurant Order** 🍽️

**Without Compose:**
```
You: "I'll have burger, fries, drink"
Waiter: "Go to counter 1 for burger"
You: Walk to counter 1
Waiter: "Go to counter 2 for fries"
You: Walk to counter 2
Waiter: "Go to counter 3 for drink"
You: Walk to counter 3
└─ Annoying!
```

**With Compose:**
```
You: "Combo meal please!"
Waiter: Brings everything together
└─ Easy!
```

### What is Redis Cache?

Think: **Short-term memory** 🧠

```
Without cache:
Request → Calculate (50ms) → Response
Request → Calculate (50ms) → Response
Request → Calculate (50ms) → Response

With cache:
Request → Calculate (50ms) → Store → Response
Request → Retrieve (2ms) → Response  ← 25x faster!
Request → Retrieve (2ms) → Response  ← 25x faster!
```

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `Dockerfile` | Build instructions (multi-stage) |
| `docker-compose.yml` | Orchestrates app + Redis |
| `app.py` | Flask API for predictions |
| `.dockerignore` | Exclude files from image |
| `requirements-docker.txt` | Python dependencies |
| `docker-build.sh` | Build image script |
| `docker-run.sh` | Run services script |
| `docker-push.sh` | Push to Docker Hub script |
| `DOCKER_GUIDE.md` | Complete guide (read this!) |
| `DOCKER_README.md` | This file (quick start) |

---

## 🚀 Next Steps

### 1. Run Locally

```bash
bash docker-run.sh
```

### 2. Test API

```bash
curl http://localhost:5000
```

### 3. Push to Docker Hub

```bash
# Login
docker login

# Edit docker-push.sh (change username)
vim docker-push.sh

# Push
bash docker-push.sh
```

### 4. Share!

Anyone can run your model:
```bash
docker pull YOUR-USERNAME/housing-price-predictor
docker run -p 5000:5000 YOUR-USERNAME/housing-price-predictor
```

---

## 🎯 Key Commands Cheat Sheet

```bash
# Start services
bash docker-run.sh
# OR
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ml-api

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Push to Docker Hub
bash docker-push.sh
```

---

## 🆘 Troubleshooting

### Port already in use?

```bash
# Stop conflicting services
docker-compose down
pkill -f 'mlflow ui'
pkill -f 'airflow'

# Or use different port:
# Edit docker-compose.yml: ports: - "8080:5000"
```

### Image too large?

```bash
# Check image size
docker images housing-price-predictor

# Multi-stage build already optimizes!
# Should be ~400-600 MB
```

### Can't connect to Redis?

```bash
# Check Redis is running
docker-compose ps redis

# View Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

---

## 📚 Learn More

- **Complete Guide:** Read `DOCKER_GUIDE.md`
- **Docker Docs:** https://docs.docker.com/
- **Docker Hub:** https://hub.docker.com/

---

## 🎊 Congratulations!

You've containerized your ML model with:

✅ **Multi-stage Dockerfile** (optimized size)
✅ **Docker Compose** (easy orchestration)
✅ **Redis caching** (fast predictions)
✅ **Production-ready** (Gunicorn server)
✅ **Portable** (runs anywhere!)

**Your model is now deployment-ready!** 🚀

Run: `bash docker-run.sh` to see it in action!
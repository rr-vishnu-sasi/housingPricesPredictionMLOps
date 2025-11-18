# 🐳 Docker Guide - Housing Price Prediction API

## 📚 Table of Contents
1. [What is Docker?](#what-is-docker)
2. [What We Built](#what-we-built)
3. [Quick Start](#quick-start)
4. [Understanding the Dockerfile](#understanding-the-dockerfile)
5. [Understanding Docker Compose](#understanding-docker-compose)
6. [How to Use](#how-to-use)
7. [Push to Docker Hub](#push-to-docker-hub)
8. [Docker Concepts Explained](#docker-concepts-explained)

---

## 🎯 What is Docker?

### Simple Analogy:

**Think of Docker like a shipping container** 🚢

**Without Docker:**
```
Your ML model on your machine:
├─ Works perfectly on YOUR computer
├─ "But it works on my machine!" syndrome
├─ Teammate tries to run it: ❌ Fails
│  "Missing Python 3.12"
│  "Wrong library version"
│  "Can't find model files"
└─ Deployment nightmare!
```

**With Docker:**
```
Your ML model in Docker:
├─ Package EVERYTHING together:
│  ├─ Python 3.12 ✓
│  ├─ All libraries ✓
│  ├─ Model files ✓
│  ├─ Code ✓
│  └─ Configuration ✓
├─ Works on ANY computer
├─ Works on YOUR machine ✓
├─ Works on TEAMMATE's machine ✓
├─ Works in PRODUCTION ✓
└─ "Runs the same everywhere!"
```

**Benefits:**
- ✅ Consistency - Same environment everywhere
- ✅ Isolation - Doesn't conflict with other software
- ✅ Portability - Run anywhere Docker runs
- ✅ Scalability - Easy to replicate

---

## 📦 What We Built

### Files Created:

```
Your Project:
├── app.py                      # Flask API for predictions
├── Dockerfile                  # Instructions to build Docker image
├── docker-compose.yml          # Orchestrates multiple containers
├── requirements-docker.txt     # Python dependencies for Docker
├── .dockerignore              # Files to exclude from image
│
└── Scripts:
    ├── docker-build.sh         # Build Docker image
    ├── docker-run.sh           # Run with Docker Compose
    └── docker-push.sh          # Push to Docker Hub
```

### Architecture:

```
┌─────────────────────────────────────────────────────────┐
│                 Docker Compose Setup                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐          ┌──────────────────┐      │
│  │   ML API       │ ←────→   │  Redis Cache     │      │
│  │  (Flask)       │  Talks   │  (In-memory DB)  │      │
│  │  Port: 5000    │   to     │  Port: 6379      │      │
│  └────────────────┘          └──────────────────┘      │
│         │                                               │
│         │ Serves predictions                            │
│         ▼                                               │
│  ┌────────────────────────────┐                        │
│  │  You (Browser/curl)        │                        │
│  │  http://localhost:5000     │                        │
│  └────────────────────────────┘                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (3 Commands)

### Prerequisites:

```bash
# Install Docker Desktop:
# macOS: https://docs.docker.com/desktop/install/mac-install/
# Windows: https://docs.docker.com/desktop/install/windows-install/
# Linux: https://docs.docker.com/engine/install/

# Verify Docker is installed:
docker --version
docker-compose --version
```

### Run Your Dockerized ML API:

```bash
# 1. Build and start services
bash docker-run.sh

# 2. Test the API
curl http://localhost:5000/health

# 3. Make a prediction
curl -X POST http://localhost:5000/predict \
  -H 'Content-Type: application/json' \
  -d '{"median_income":8.3,"housing_median_age":41,"total_rooms":880,"total_bedrooms":129,"population":322,"households":126,"latitude":37.88,"longitude":-122.23,"ocean_proximity":"NEAR BAY"}'
```

**Expected output:**
```json
{
  "predicted_price": 452600.65,
  "predicted_price_formatted": "$452,600.65",
  "cached": false
}
```

---

## 📖 Understanding the Dockerfile

### What is a Dockerfile?

**Think of it like a recipe** 🍳

```
Recipe for Chocolate Cake:
1. Get ingredients (flour, sugar, cocoa)
2. Mix ingredients
3. Bake at 350°F
4. Serve

Dockerfile for ML API:
1. Get base image (Python 3.12)
2. Install dependencies
3. Copy code and model
4. Run Flask app
```

### Multi-Stage Build Explained:

**Why two stages?**

```
STAGE 1 (Builder):
├─ Large image (~2 GB)
├─ Has compilers (gcc, g++)
├─ Installs all dependencies
├─ Compiles Python packages
└─ Gets DISCARDED!

STAGE 2 (Production):
├─ Small image (~500 MB)
├─ No compilers (not needed!)
├─ Just runtime + app
├─ This is what you deploy!
└─ 4x smaller = faster downloads!
```

**Visual:**

```
┌──────────────────────────────┐
│  STAGE 1: Builder (LARGE)    │
│  python:3.12-slim            │
│  + gcc, g++, make            │  ← Build tools
│  + All dependencies          │  ← Compiled packages
│  + Source code               │
│  Size: ~2 GB                 │
└──────────┬───────────────────┘
           │ Copy only what's needed
           ▼
┌──────────────────────────────┐
│  STAGE 2: Production (SMALL) │
│  python:3.12-slim            │
│  + Installed packages        │  ← From builder
│  + App code                  │  ← From builder
│  + Model files               │  ← From builder
│  Size: ~500 MB               │  ← 75% smaller!
└──────────────────────────────┘
      This is your final image!
```

### Dockerfile Walkthrough:

```dockerfile
# STAGE 1: Builder
FROM python:3.12-slim as builder
# ↑ Start with Python base image
# "as builder" = name this stage for reference

WORKDIR /build
# ↑ All commands run in /build directory

RUN apt-get update && apt-get install gcc g++ make
# ↑ Install build tools (needed to compile packages)

COPY requirements-docker.txt .
# ↑ Copy just requirements first (Docker layer caching!)

RUN pip install -r requirements-docker.txt
# ↑ Install all Python packages

COPY . .
# ↑ Copy all your code

# STAGE 2: Production
FROM python:3.12-slim
# ↑ Fresh Python image (small!)

WORKDIR /app
# ↑ Runtime directory

COPY --from=builder /opt/venv /opt/venv
# ↑ Copy installed packages FROM builder stage

COPY --from=builder /build/app.py .
COPY --from=builder /build/models ./models
# ↑ Copy only what's needed to run

EXPOSE 5000
# ↑ Document which port the app uses

CMD ["gunicorn", "app:app"]
# ↑ Command to start the app
```

---

## 🎼 Understanding Docker Compose

### What is Docker Compose?

**Think: Orchestra Conductor** 🎵

**Without Compose:**
```bash
# Start Redis manually
docker run -d -p 6379:6379 redis

# Start ML API manually
docker run -d -p 5000:5000 --link redis ml-api

# Complex! Error-prone! Hard to remember!
```

**With Compose:**
```bash
# Start EVERYTHING with one command
docker-compose up

# Stops, starts, links automatically!
```

### docker-compose.yml Explained:

```yaml
services:
  # Service 1: Redis Cache
  redis:
    image: redis:7-alpine      # ← Pre-built Redis image
    ports:
      - "6379:6379"             # ← Port mapping (host:container)
    networks:
      - ml-network              # ← Connect to shared network

  # Service 2: ML API
  ml-api:
    build: .                    # ← Build from Dockerfile
    ports:
      - "5000:5000"             # ← Port mapping
    environment:
      - REDIS_HOST=redis        # ← Can reference by service name!
    depends_on:
      - redis                   # ← Wait for Redis to start
    networks:
      - ml-network              # ← Same network as Redis

networks:
  ml-network:                   # ← Private network for services
```

**Magic of Docker Compose:**
- ✅ Services can talk by name (`redis`, `ml-api`)
- ✅ Automatic networking
- ✅ Dependency management
- ✅ One command to rule them all!

---

## 🚀 How to Use

### Option 1: Docker Compose (Recommended!)

```bash
# Build and start everything
bash docker-run.sh

# Or manually:
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ml-api

# Stop everything
docker-compose down
```

### Option 2: Docker Run (Single Container)

```bash
# Build image
bash docker-build.sh

# Run without Redis
docker run -p 5000:5000 housing-price-predictor:latest

# Run with custom port
docker run -p 8080:5000 housing-price-predictor:latest
# Access at: http://localhost:8080
```

### Option 3: Build Manually

```bash
# Build the image
docker build -t housing-price-predictor:latest .

# Run it
docker run -d -p 5000:5000 --name ml-api housing-price-predictor:latest

# Check logs
docker logs -f ml-api

# Stop
docker stop ml-api
docker rm ml-api
```

---

## 🧪 Testing the API

### 1. Health Check

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "loaded",
  "redis": "connected"
}
```

### 2. API Info

```bash
curl http://localhost:5000/
```

**Shows:** All available endpoints and examples

### 3. Single Prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "median_income": 8.3252,
    "housing_median_age": 41.0,
    "total_rooms": 880,
    "total_bedrooms": 129,
    "population": 322,
    "households": 126,
    "latitude": 37.88,
    "longitude": -122.23,
    "ocean_proximity": "NEAR BAY"
  }'
```

**Response:**
```json
{
  "predicted_price": 452600.65,
  "predicted_price_formatted": "$452,600.65",
  "input_data": {...},
  "cached": false
}
```

### 4. Batch Predictions

```bash
curl -X POST http://localhost:5000/predict/batch \
  -H 'Content-Type: application/json' \
  -d '{
    "houses": [
      {"median_income":8.3,"housing_median_age":41,"total_rooms":880,"total_bedrooms":129,"population":322,"households":126,"latitude":37.88,"longitude":-122.23,"ocean_proximity":"NEAR BAY"},
      {"median_income":7.2,"housing_median_age":52,"total_rooms":1274,"total_bedrooms":235,"population":558,"households":219,"latitude":37.85,"longitude":-122.24,"ocean_proximity":"NEAR BAY"}
    ]
  }'
```

### 5. Cache Statistics

```bash
curl http://localhost:5000/cache/stats
```

**Response:**
```json
{
  "connected": true,
  "keys": 15,
  "memory_used": "1.2M",
  "uptime_seconds": 3600
}
```

---

## 🐳 Push to Docker Hub

### Step 1: Create Docker Hub Account

1. Go to: https://hub.docker.com
2. Sign up (free account)
3. Remember your username

### Step 2: Login

```bash
docker login
# Enter your Docker Hub username and password
```

### Step 3: Update Push Script

Edit `docker-push.sh`:
```bash
# Line 11: Change this to YOUR Docker Hub username
DOCKERHUB_USERNAME="your-dockerhub-username"
```

### Step 4: Push

```bash
# Push latest version
bash docker-push.sh

# Or push with specific tag
bash docker-push.sh v1.0.0
```

### Step 5: Share!

Your image is now public:
```
https://hub.docker.com/r/YOUR-USERNAME/housing-price-predictor
```

Anyone can run it:
```bash
docker pull YOUR-USERNAME/housing-price-predictor:latest
docker run -p 5000:5000 YOUR-USERNAME/housing-price-predictor:latest
```

---

## 📊 Docker Concepts Explained

### 1. **Images vs Containers**

**Image** = Blueprint (like a class in programming)
```
housing-price-predictor:latest
├─ Python 3.12
├─ All libraries
├─ Your code
├─ Model files
└─ Ready to run!
```

**Container** = Running instance (like an object)
```
From one image, create multiple containers:
Container 1: Running on port 5000
Container 2: Running on port 5001
Container 3: Running on port 5002
All from same image!
```

**Analogy:**
```
Image = Cookie cutter 🍪
Container = Actual cookie

One cutter → Many cookies!
One image → Many containers!
```

---

### 2. **Layers**

Each Dockerfile instruction creates a layer:

```dockerfile
FROM python:3.12-slim     # Layer 1: Base (200 MB)
RUN pip install pandas    # Layer 2: Pandas (50 MB)
COPY app.py .             # Layer 3: Your app (1 KB)
```

**Layers are cached!**

```
First build:
├─ Layer 1: Downloaded (2 min)
├─ Layer 2: Downloaded (1 min)
└─ Layer 3: Built (1 sec)
Total: 3 minutes

Second build (only changed app.py):
├─ Layer 1: CACHED! (0 sec)
├─ Layer 2: CACHED! (0 sec)
└─ Layer 3: Rebuilt (1 sec)
Total: 1 second!
```

---

### 3. **Port Mapping**

```
-p 5000:5000
   ↑     ↑
   │     └─ Container port (inside Docker)
   └──────── Host port (your machine)

Example:
-p 8080:5000
   └─ Access via http://localhost:8080
      Routes to container's port 5000
```

---

### 4. **Volumes**

**Purpose:** Persist data outside containers

```
Without volumes:
Container created → Has data
Container deleted → Data LOST! ❌

With volumes:
Container created → Stores data in volume
Container deleted → Data SAFE in volume ✓
New container → Mounts volume → Data still there!
```

**In docker-compose.yml:**
```yaml
volumes:
  redis-data:    # Named volume
    name: housing-redis-data

services:
  redis:
    volumes:
      - redis-data:/data  # Mount volume
```

---

### 5. **Networks**

**Purpose:** Let containers talk to each other

```
┌─────────────────────────────────┐
│    ml-network (Docker Network)   │
│                                  │
│  ┌─────────┐      ┌──────────┐  │
│  │ ML API  │ ←──→ │  Redis   │  │
│  └─────────┘      └──────────┘  │
│       Can talk by service name!  │
└─────────────────────────────────┘

ml-api can connect to: redis:6379
(Not localhost! Service name!)
```

---

## 🔧 Common Commands

### Docker:

```bash
# List images
docker images

# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop <container-name>

# Remove container
docker rm <container-name>

# Remove image
docker rmi <image-name>

# View logs
docker logs <container-name>
docker logs -f <container-name>  # Follow mode

# Execute command in container
docker exec -it <container-name> bash
docker exec -it <container-name> python
```

### Docker Compose:

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs
docker-compose logs -f ml-api
docker-compose logs -f redis

# Restart a service
docker-compose restart ml-api

# View running services
docker-compose ps

# Execute command
docker-compose exec ml-api bash
docker-compose exec ml-api python
```

---

## 🎯 Development Workflow

### Making Changes:

```bash
# 1. Edit code
vim app.py

# 2. Rebuild and restart
docker-compose up --build

# That's it! Changes applied!
```

### Debugging:

```bash
# View API logs
docker-compose logs -f ml-api

# Enter container
docker-compose exec ml-api bash

# Inside container, you can:
ls -la                    # List files
python                    # Run Python
pip list                  # See installed packages
cat /app/models/...       # Check model files
```

---

## 📦 What's Inside the Container?

```
Container Filesystem:
/app/
├── app.py                 # Flask API
├── src/                   # Your source code
│   ├── data/
│   ├── features/
│   ├── models/
│   └── utils.py
├── models/                # Model artifacts
│   └── saved_models/
│       ├── model_*.joblib
│       ├── scaler.joblib
│       └── encoder.joblib
└── config/
    └── config.yaml
```

**NOT included** (thanks to .dockerignore):
- Virtual environments (.venv/)
- Data files (data/*.csv)
- Logs
- Documentation
- Git history

**Result:** Lean, production-ready image!

---

## 🎓 Docker Learning Path

### Beginner Level:

```bash
# 1. Run pre-built image
docker run hello-world

# 2. Run your ML API
bash docker-run.sh

# 3. View running containers
docker ps

# 4. Stop containers
docker-compose down
```

### Intermediate Level:

```bash
# 1. Build custom image
bash docker-build.sh

# 2. Inspect image
docker inspect housing-price-predictor:latest

# 3. Enter running container
docker-compose exec ml-api bash

# 4. View logs
docker-compose logs -f ml-api
```

### Advanced Level:

```bash
# 1. Optimize Dockerfile
# 2. Add monitoring (Prometheus)
# 3. Set up orchestration (Kubernetes)
# 4. Implement CI/CD with Docker
```

---

## ⚡ Performance: Redis Caching

### How Caching Works:

```
Request 1 (First time):
Client → API → Preprocess → Model → Predict → Redis stores → Response
Time: 50ms

Request 2 (Same input):
Client → API → Redis retrieves → Response
Time: 2ms (25x faster!)
```

### Testing Cache:

```bash
# First request (slow)
time curl -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{...}'
# real	0m0.050s

# Second request (fast!)
time curl -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{...}'
# real	0m0.002s

# Response shows: "cached": true
```

---

## 🎯 Deliverable Checklist

For your GitHub repository:

- [x] ✅ Dockerfile (multi-stage build)
- [x] ✅ docker-compose.yml (app + Redis)
- [x] ✅ Flask API (app.py)
- [x] ✅ Helper scripts (build, run, push)
- [x] ✅ .dockerignore (lean images)
- [x] ✅ requirements-docker.txt
- [x] ✅ Documentation (this guide!)

---

## 📝 README Snippet

Add this to your main README.md:

````markdown
## 🐳 Docker Deployment

### Quick Start

```bash
# Build and run with Docker Compose
bash docker-run.sh

# Access API at http://localhost:5000
```

### Services

- **ML API**: Flask app serving predictions (port 5000)
- **Redis**: Cache for faster responses (port 6379)

### Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f ml-api

# Push to Docker Hub
bash docker-push.sh
```

See `DOCKER_GUIDE.md` for complete documentation.
````

---

## 🎉 Summary

You now have:

✅ **Dockerized ML API** - Runs anywhere
✅ **Multi-stage build** - Optimized image size
✅ **Redis caching** - 25x faster responses
✅ **Docker Compose** - Easy orchestration
✅ **Production-ready** - Gunicorn WSGI server
✅ **Health checks** - Kubernetes-compatible
✅ **Documentation** - Complete guide

**Next:** Run `bash docker-run.sh` and test it!

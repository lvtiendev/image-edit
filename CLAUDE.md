# Chat To Edit Image

A full-stack web application that allows users to generate and edit images through natural language text messages. The application combines AI-powered image generation and editing capabilities with an intuitive chat interface.

## 🎯 Project Overview

This project consists of two main components:

1. **Backend Server** (`/server`): A FastAPI-based Python server that handles AI image generation and editing
2. **Frontend Webapp** (`/webapp`): A Next.js React application providing the user interface for chat-based image manipulation

### Key Features

- **Dual AI Model Support**: Choose between Stable Diffusion 2.1 or FLUX.1-dev models
- **Text-to-Image Generation**: Generate images from text prompts
- **Image Editing**: Edit existing images through text descriptions using img2img pipeline
- **Chat Interface**: Natural language interaction with command syntax (`generate: <prompt>`)
- **Image History**: Track and revisit previously generated/edited images with click-to-restore
- **Real-time Processing**: Live chat interface with server health monitoring
- **GPU Acceleration**: Optimized for NVIDIA GPU acceleration with automatic CPU fallback
- **Model Hot-Swapping**: Switch between models via environment variable or command line

### Development Documentation

For AI agent development workflows and detailed architecture, see **[AGENTS.md](./AGENTS.md)**.

## 🛠 Tech Stack

### Backend (Python)
- **Framework**: FastAPI 0.115.6+
- **AI/ML**:
  - Diffusers 0.32.1+ (Hugging Face)
  - Transformers 4.47.1+
  - PyTorch 2.5.1+
  - Accelerate 1.2.1+
  - Stable Diffusion 2.1 (default model)
  - FLUX.1-dev (alternative model)
- **Image Processing**: Pillow 11.0.0+
- **Server**: Uvicorn 0.34.0+
- **Package Management**: UV (modern Python package manager)
- **Base Image**: NVIDIA CUDA 12.0.0 (Ubuntu 22.04)

### Frontend (TypeScript/React)
- **Framework**: Next.js 15.1.3
- **React**: 19.0.0
- **Styling**: Tailwind CSS 3.4.1
- **UI Components**:
  - Radix UI (ScrollArea, Slot)
  - Lucide React (icons)
  - Class Variance Authority
- **Chat Integration**: AI SDK 4.0.22
- **Validation**: Zod 3.24.1
- **Package Manager**: Yarn 1.22.22
- **Linting**: ESLint 9

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **GPU Support**: NVIDIA Docker runtime
- **Development**: Hot reload for both frontend and backend

## 🚀 Local Development Setup

### Prerequisites

- **Docker & Docker Compose**: For containerized development
- **NVIDIA GPU** (recommended): For optimal performance
- **NVIDIA Docker Runtime**: For GPU acceleration
- **Node.js 20+** (optional): For local frontend development
- **Python 3.10+** (optional): For local backend development

### Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd image-edit
   ```

2. **Start the application** (Stable Diffusion 2.1 model):
   ```bash
   docker compose up --build
   # Or use: make up
   ```

   **To use FLUX.1-dev model instead:**
   ```bash
   docker compose -f docker-compose.flux.yml up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Makefile Commands

The project includes a Makefile for common Docker operations:
```bash
make up    # Start all services with docker compose
make down  # Stop all services
make logs  # View and follow logs from all services
make clean # Stop services and remove Docker volumes
```

### Development Mode

#### Backend Development

1. **Navigate to server directory**:
   ```bash
   cd server
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run the server** (default: Stable Diffusion 2.1):
   ```bash
   uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

   **To use FLUX.1-dev model:**
   ```bash
   uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000 flux
   ```

   **Or set environment variable:**
   ```bash
   export MODEL_TYPE=flux
   uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Development

1. **Navigate to webapp directory**:
   ```bash
   cd webapp
   ```

2. **Install dependencies**:
   ```bash
   yarn install
   ```

3. **Set environment variable**:
   ```bash
   export NEXT_PUBLIC_IMAGE_SERVER_URL=http://localhost:8000
   ```

4. **Run the development server**:
   ```bash
   yarn dev
   ```

### Environment Variables

#### Backend
- `MODEL_TYPE`: Model selection - `stable-diffusion` (default) or `flux`
- `HF_TOKEN`: Hugging Face token for accessing gated models (optional)
  - Get your token at: https://huggingface.co/settings/tokens
  - Required for gated models like FLUX.1-dev
  - Never commit this token to git!
- `DEVICE_MAP`: GPU device mapping strategy - `balanced` (default), `sequential`, or `none`
  - Controls how to distribute model across multiple GPUs
  - See Multi-GPU Setup section below for details
- `QUANTIZATION`: Model quantization for FLUX - `8bit` (default), `4bit`, or `none`
  - Reduces memory usage by 2-4x with minimal quality loss
  - Only applies to FLUX model on CUDA GPUs
  - See Quantization section below for details
- `MAX_MEMORY`: Optional memory limit per GPU (format: `0:10,1:10`)
  - Limits GPU memory usage in GB per device
  - Leave empty for automatic management

#### Frontend
- `NEXT_PUBLIC_IMAGE_SERVER_URL`: Backend server URL (default: http://localhost:8000)

### 🔐 Secure Token Management

The Hugging Face token (`HF_TOKEN`) is required for accessing gated models. Here's how to set it up securely:

#### Local Development

1. **Create a `.env` file** in the project root (already in `.gitignore`):
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your token**:
   ```env
   HF_TOKEN=hf_your_token_here
   MODEL_TYPE=stable-diffusion
   ```

3. **Get your token** from: https://huggingface.co/settings/tokens

#### Docker Compose (Recommended)

The `docker-compose.yml` and `docker-compose.flux.yml` files automatically:
- Read from `.env` file (via `env_file`)
- Pass the token to the server container
- Never expose it in logs or commits

#### Direct Export (Local Python Development)

```bash
export HF_TOKEN=hf_your_token_here
cd server
uv run uvicorn server:app --reload
```

#### Production Security

For production deployments, use:
- **Docker Secrets** (Docker Swarm)
- **Kubernetes Secrets** (K8s)
- **Cloud Secret Managers** (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
- **CI/CD Variables** (GitHub Secrets, GitLab CI/CD variables)

**Never:**
- Commit `.env` files to git (they're in `.gitignore`)
- Share tokens in chat, email, or public forums
- Embed tokens in Docker images
- Log tokens in output

### 🖥️ Multi-GPU Setup

The application supports automatic multi-GPU utilization to handle large models like FLUX that don't fit on a single GPU.

#### How It Works

The server uses **Hugging Face Accelerate** to automatically distribute models across all available GPUs:

- **Automatic Detection**: Detects all GPUs on startup and displays their specs
- **Smart Distribution**: Automatically splits model layers across GPUs
- **Memory Management**: Balances memory usage to prevent OOM errors
- **Lazy Loading**: Only loads text2img pipeline at startup; img2img loads on first edit
- **Zero Config**: Works out of the box with `DEVICE_MAP=balanced`

#### Lazy Loading for Better Memory Management

The application uses **lazy loading** to optimize memory usage:

**At Startup:**
- Only loads `text2img` pipeline (for image generation)
- Memory usage: ~6-8GB for FLUX with 8-bit quantization (fits easily on any GPU)
- Startup is faster and more reliable

**On First Edit Request:**
- Automatically loads `img2img` pipeline (for image editing)
- One-time delay while loading (~30-60 seconds)
- After loading, both pipelines are cached and ready

**Subsequent Edits:**
- Both pipelines loaded and ready
- Fast iteration for repeated edits
- Total memory: ~12-16GB with 8-bit quantization (spreads across both GPUs)

**Benefits for Your Workflow:**
- ✅ Startup succeeds even with limited GPU memory
- ✅ Perfect for "generate once, edit many times" workflow
- ✅ No manual intervention needed
- ✅ Automatic pipeline loading when needed

#### 🎛️ Quantization for Memory Efficiency

**NEW:** The application now supports **8-bit quantization** to dramatically reduce memory usage for FLUX models.

**What is Quantization?**
Quantization reduces model precision from 16-bit (fp16) to 8-bit (int8), cutting memory usage by ~2x with minimal quality loss.

**Memory Comparison (FLUX.1-schnell):**

| Configuration | Memory Per Pipeline | Total Memory (Both) |
|---------------|-------------------|---------------------|
| fp16 (no quant) | ~12-15GB | ~24-30GB |
| **8-bit (default)** | **~6-8GB** | **~12-16GB** ✅ |
| 4-bit | ~3-4GB | ~6-8GB (more quality loss) |

**Configuration:**

```env
# In .env file
QUANTIZATION=8bit  # Options: 8bit (default), 4bit, none
```

**QUANTIZATION Options:**

- **`8bit`** (Recommended): Best balance
  - 2x memory reduction
  - Minimal quality loss (imperceptible)
  - Fast inference

- **`4bit`: Maximum memory savings
  - 4x memory reduction
  - More noticeable quality degradation
  - Slightly slower inference

- **`none`: Full precision (original)
  - Highest quality
  - Highest memory usage
  - May cause OOM on limited VRAM

**When to Use Quantization:**

✅ **Use 8-bit quantization when:**
- Running FLUX on GPUs with <24GB VRAM
- Getting CUDA out of memory errors
- Want to run both pipelines simultaneously
- Most production use cases

❌ **Use `none` when:**
- You have abundant VRAM (48GB+ per GPU)
- Need absolute maximum quality
- Doing professional/production work where quality is critical

**Quality Impact:**

- **8-bit**: ~1-2% quality loss (imperceptible to most users)
- **4-bit**: ~5-10% quality loss (noticeable on close inspection)

**Performance:**

- **Memory**: 8-bit uses 50% less memory
- **Speed**: Similar or slightly faster than fp16
- **Quality**: Virtually identical for 8-bit

**Recommended Setup for 2x24GB GPUs:**

```env
MODEL_TYPE=flux
DEVICE_MAP=balanced
QUANTIZATION=8bit
# No MAX_MEMORY needed
```

This configuration will:
- Use ~6-8GB per pipeline (total ~12-16GB after first edit)
- Fit easily on 2x24GB GPUs
- Provide excellent quality
- Enable both generation and editing

#### Configuration Options

Set in your `.env` file:

```env
# Device Mapping Strategy
DEVICE_MAP=balanced  # Options: balanced, sequential, none

# Quantization (FLUX only)
QUANTIZATION=8bit  # Options: 8bit, 4bit, none

# Optional: Manually limit memory per GPU (in GB)
MAX_MEMORY=0:10,1:10  # GPU 0: 10GB, GPU 1: 10GB
```

**DEVICE_MAP Options:**

- **`balanced`** (Recommended): Distribute evenly across all GPUs
  - Best for most multi-GPU setups
  - Balances load based on available memory
  - Handles 2+ GPUs seamlessly

- **`sequential`: Fill GPUs in order (0, then 1, then 2...)
  - Use if you have heterogeneous GPUs (different VRAM sizes)
  - Fills one GPU before moving to next

- **`none`**: Single GPU mode (disables multi-GPU)
  - Use for debugging or if you only have 1 GPU

**Note:** The `auto` option is not supported by the current version of accelerate. Use `balanced` instead.

#### Example Configurations

**Two 24GB GPUs for FLUX with 8-bit quantization (Recommended):**
```env
MODEL_TYPE=flux
DEVICE_MAP=balanced
QUANTIZATION=8bit
# No MAX_MEMORY needed - fits easily
```

**Two 12GB GPUs with manual limits:**
```env
MODEL_TYPE=flux
DEVICE_MAP=balanced
QUANTIZATION=8bit
MAX_MEMORY=0:10,1:10  # Leave 2GB headroom
```

**Heterogeneous GPUs (24GB + 12GB):**
```env
MODEL_TYPE=flux
DEVICE_MAP=sequential
QUANTIZATION=8bit
MAX_MEMORY=0:20,1:10  # Match actual GPU sizes
```

#### Verifying Multi-GPU Usage

Check server logs on startup:

```
Using device: cuda
Detected 2 GPU(s)
  GPU 0: NVIDIA GeForce RTX 4090 (24.0GB total)
  GPU 1: NVIDIA GeForce RTX 3090 (24.0GB total)
Device map strategy: balanced
Using 8-bit quantization to reduce memory usage
Loading Flux text-to-image model with multi-GPU with 8-bit quantization support...
Note: img2img pipeline will be loaded on first edit request
Flux text-to-image model loaded successfully with reduced memory footprint
```

Or check GPU usage while generating:

```bash
# Terminal 1: Watch GPU memory
watch -n 0.5 nvidia-smi

# Terminal 2: Generate an image
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a beautiful landscape"}'
```

Both GPUs should show memory usage during generation.

#### Troubleshooting Multi-GPU

**Still getting OOM errors?**
1. Reduce `MAX_MEMORY` limits (try 8GB per GPU instead of 10GB)
2. Set `MAX_MEMORY=0:8,1:8` (leave more headroom)
3. Use Stable Diffusion instead of FLUX (smaller model)

**Only one GPU being used?**
- Check `NVIDIA_VISIBLE_DEVICES=all` in docker-compose.yml
- Verify `count: all` in GPU reservations
- Check server logs show both GPUs

**Performance slower than expected?**
- First run is slower (downloading/model loading)
- Check `nvidia-smi` - both GPUs should be utilized
- Try `DEVICE_MAP=balanced` for better distribution
- PCIe bandwidth matters - GPUs on same PCIe slot better

### Testing

The project includes a basic integration test script:
```bash
./test-dev.sh  # Test the development setup
```

This script:
1. Stops any existing containers
2. Starts the development environment
3. Waits for services to initialize
4. Tests server health endpoint
5. Tests webapp accessibility

## 📁 Project Structure

```
image-edit/
├── server/                      # Python FastAPI backend
│   ├── server.py               # Main FastAPI application
│   ├── client_edit.py          # Image editing client
│   ├── client_generate.py      # Image generation client
│   ├── pyproject.toml          # Python dependencies
│   ├── Dockerfile              # Backend container config
│   └── README.md
├── webapp/                     # Next.js frontend
│   ├── src/
│   │   ├── app/                # Next.js app directory
│   │   │   ├── page.tsx        # Main app page
│   │   │   └── layout.tsx      # App layout
│   │   ├── components/         # React components
│   │   │   ├── ui/             # Reusable UI components
│   │   │   ├── ChatPanel.tsx   # Chat interface
│   │   │   ├── ImagePanel.tsx  # Image display/upload
│   │   │   └── HistoryPanel.tsx # Image history
│   │   ├── lib/                # Utility functions
│   │   └── types/              # TypeScript type definitions
│   ├── package.json            # Node.js dependencies
│   ├── Dockerfile              # Production container config
│   ├── Dockerfile.dev          # Development container config
│   ├── next.config.ts          # Next.js configuration
│   ├── tailwind.config.ts      # Tailwind CSS config
│   └── README.md
├── docker-compose.yml          # Main orchestration (SD model)
├── docker-compose.flux.yml     # Alternative orchestration (FLUX model)
├── docker-compose.override.yml.example  # Override config example
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns (includes .env)
├── Makefile                    # Development commands
├── test-dev.sh                 # Development setup test script
├── AGENTS.md                   # AI agent development guide
├── CLAUDE.md                   # This file - project documentation
└── README.md                   # Main project README
```

## 🔧 API Endpoints

### Backend API (Port 8000)

- `POST /generate`: Generate images from text prompts
  - Body: `{ "prompt": string, "negative_prompt": string?, "num_inference_steps": number?, "guidance_scale": number? }`
  - Returns: `{ "status": "success", "image": "base64_encoded_image" }`
  - Note: For FLUX model, `negative_prompt` is ignored

- `POST /edit`: Edit images using text prompts
  - Body: FormData with `file`, `prompt`, `strength`, `num_inference_steps`, `guidance_scale`, `negative_prompt`
  - Returns: `{ "status": "success", "image": "base64_encoded_image" }`
  - Note: For FLUX model, `negative_prompt` is ignored

- `GET /health`: Health check endpoint
  - Returns: `{ "status": "healthy", "models_loaded": boolean }`

- `GET /models`: Get information about currently loaded model
  - Returns: `{ "model": "stable-diffusion" | "flux", "models_loaded": boolean }`

## 🎨 Usage

1. **Generate Images**: Type `generate: your prompt here` in the chat
2. **Edit Images**: Upload an image first, then type your editing prompt
3. **View History**: Browse previously generated/edited images in the history panel
4. **Replace Images**: Click on any image in history to make it current

## 🐳 Docker Configuration

### Backend Container
- **Base**: NVIDIA CUDA 12.0.0 (Ubuntu 22.04)
- **GPU Support**: Automatic CUDA detection and optimization
- **Memory**: Optimized for GPU memory usage with attention slicing
- **Model Selection**: Set via `MODEL_TYPE` environment variable or docker-compose file

### Frontend Container
- **Production**: Node.js 20 slim with production-optimized Next.js build
- **Development**: Separate `Dockerfile.dev` with hot reload via volume mounting
- **Port**: 3000

### Docker Compose Files
- **docker-compose.yml**: Main configuration using Stable Diffusion 2.1 model
- **docker-compose.flux.yml**: Alternative configuration using FLUX.1-dev model
- **docker-compose.override.yml.example**: Template for local development overrides

### Docker Compose Features
- **GPU Access**: Automatic GPU passthrough to backend via NVIDIA runtime
- **Service Dependencies**: Frontend waits for backend health check
- **Environment**: Automatic service discovery between containers
- **Volume Mounts**: Development mode hot-reloads code changes

## 🔍 Development Notes

### Model Selection
- **Startup Configuration**: Models are loaded at server startup, not per-request
- **Selection Methods**:
  - Command line argument: `uvicorn server:app flux`
  - Environment variable: `MODEL_TYPE=flux`
  - Docker Compose file: Set in service environment
- **Default Model**: Stable Diffusion 2.1 if not specified

### Model Differences
- **Stable Diffusion 2.1**:
  - Supports negative prompts
  - Faster inference (typically 15-25 steps)
  - Lower GPU memory requirement (~8GB)
  - Better for quick iterations

- **FLUX.1-dev**:
  - Does not support negative prompts (parameter ignored)
  - Higher quality output (typically 28-50 steps)
  - Higher GPU memory requirement (~12-16GB recommended)
  - Better for final image generation

### Architecture Notes
- **GPU Memory**: Automatic CUDA detection with CPU fallback
- **Memory Optimization**: Attention slicing enabled for reduced GPU memory
- **Model Loading**: Models loaded once at startup (first run downloads model weights)
- **CORS**: Currently configured for development (allows all origins)
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Image Format**: All images processed as PNG for consistency
- **State Management**: Frontend uses AI SDK's useChat hook for chat state
- **Health Monitoring**: Frontend polls `/health` endpoint on mount

## 🚨 Production Considerations

### Security
- **CORS Configuration**: Currently allows all origins - restrict to specific domains
- **File Upload Validation**: Add size limits and format validation
- **Rate Limiting**: Implement API rate limiting to prevent abuse
- **Authentication**: Add user authentication if deploying publicly
- **Input Sanitization**: Validate all user prompts and inputs

### Performance
- **Model Caching**: Models downloaded on first run - consider pre-caching for deployments
- **GPU Resource Limits**: Set appropriate memory reservations in docker-compose
- **Load Balancing**: Consider multiple backend instances for high traffic
- **CDN**: Serve static assets via CDN for better performance
- **Image Optimization**: Consider image compression before transmission

### Monitoring & Logging
- **Structured Logging**: Implement JSON-based logging for parsing
- **Metrics**: Track generation times, GPU utilization, error rates
- **Health Checks**: Use `/health` endpoint for load balancer checks
- **Error Tracking**: Integrate with error tracking service (Sentry, etc.)

### Deployment
- **Image Optimization**: Use multi-stage builds to reduce image sizes
- **Environment Variables**: Use secrets management for sensitive data
- **GPU Configuration**: Ensure proper NVIDIA driver and runtime versions
- **Model Storage**: Consider persistent volume for model cache
- **Backup Strategy**: Backup user-generated content if persistence is added

### Testing
- **Unit Tests**: Currently not implemented - add pytest for backend
- **Integration Tests**: Test API endpoints with sample data
- **E2E Tests**: Consider Playwright or Cypress for user flows
- **Load Testing**: Test performance under concurrent requests

## 📝 License

This is a toy project for educational purposes. Please check individual library licenses for commercial use.

## 🐛 Troubleshooting

### Common Issues

**Server won't start / Model loading fails:**
- Check GPU availability: `nvidia-smi` (should show GPU info)
- Ensure NVIDIA Docker runtime is installed
- Verify sufficient GPU memory (8GB+ for SD, 12GB+ for FLUX)
- First run downloads model weights (~5GB) - may take time

**Gated model access denied (HF_TOKEN issues):**
- Ensure you've accepted the model license on Hugging Face
- Verify `HF_TOKEN` is set in `.env` file
- Check token has correct permissions (Read access)
- For Docker: Verify `.env` file is in project root
- Restart containers after adding token: `docker compose down && docker compose up`
- Check server logs for: "HF_TOKEN found - will use for authentication"

**Frontend can't connect to backend:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check `NEXT_PUBLIC_IMAGE_SERVER_URL` environment variable
- Ensure no firewall blocking port 8000

**Docker GPU not working:**
- Install NVIDIA Container Toolkit: `sudo apt-get install -y nvidia-container-toolkit`
- Restart Docker daemon: `sudo systemctl restart docker`
- Verify GPU passthrough: `docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi`

**Out of memory errors:**
- Reduce inference steps in generation request
- Use Stable Diffusion model instead of FLUX (lower memory requirement)
- Close other GPU-intensive applications
- For multi-GPU systems: Check `DEVICE_MAP=auto` is set in `.env`
- Set `MAX_MEMORY=0:8,1:8` to limit GPU memory (adjust values for your GPUs)
- Verify both GPUs are detected in server logs
- Try `DEVICE_MAP=none` to use single GPU if multi-GPU isn't working
- Restart Docker: `docker compose down && docker compose up`

**Slow image generation:**
- Check GPU is being utilized: `nvidia-smi` during generation
- Reduce `num_inference_steps` parameter (default 50, try 20-30)
- Ensure using GPU not CPU (CPU fallback is very slow)
- Consider upgrading GPU if older model

### Getting Help

- Check server logs: `docker compose logs -f server`
- Check webapp logs: `docker compose logs -f webapp`
- Review AGENTS.md for architecture details
- Open an issue on GitHub with logs and error messages

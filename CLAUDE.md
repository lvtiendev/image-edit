# Chat To Edit Image

A full-stack web application that allows users to generate and edit images through natural language text messages. The application combines AI-powered image generation and editing capabilities with an intuitive chat interface.

## 🎯 Project Overview

This project consists of two main components:

1. **Backend Server** (`/server`): A FastAPI-based Python server that handles AI image generation and editing using Stable Diffusion models
2. **Frontend Webapp** (`/webapp`): A Next.js React application providing the user interface for chat-based image manipulation

### Key Features

- **Text-to-Image Generation**: Generate images from text prompts using Stable Diffusion 2.1
- **Image Editing**: Edit existing images through text descriptions using img2img pipeline
- **Chat Interface**: Natural language interaction for image operations
- **Image History**: Track and revisit previously generated/edited images
- **Real-time Processing**: Live chat interface with immediate feedback
- **GPU Acceleration**: Optimized for NVIDIA GPU acceleration when available

## 🛠 Tech Stack

### Backend (Python)
- **Framework**: FastAPI 0.115.6+
- **AI/ML**:
  - Diffusers 0.32.1+ (Hugging Face)
  - Transformers 4.47.1+
  - PyTorch 2.5.1+
  - Accelerate 1.2.1+
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

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

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

3. **Run the server**:
   ```bash
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
- No specific environment variables required (uses default Stable Diffusion model)

#### Frontend
- `NEXT_PUBLIC_IMAGE_SERVER_URL`: Backend server URL (default: http://localhost:8000)

## 📁 Project Structure

```
image-edit/
├── server/                 # Python FastAPI backend
│   ├── server.py          # Main FastAPI application
│   ├── client_edit.py     # Image editing client
│   ├── client_generate.py # Image generation client
│   ├── pyproject.toml     # Python dependencies
│   ├── Dockerfile         # Backend container config
│   └── README.md
├── webapp/                # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   │   ├── ui/        # Reusable UI components
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── ImagePanel.tsx
│   │   │   └── HistoryPanel.tsx
│   │   ├── lib/           # Utility functions
│   │   └── types/         # TypeScript type definitions
│   ├── package.json       # Node.js dependencies
│   ├── Dockerfile         # Frontend container config
│   └── tailwind.config.ts
├── docker-compose.yml     # Multi-service orchestration
├── Makefile              # Development commands
└── README.md
```

## 🔧 API Endpoints

### Backend API (Port 8000)

- `POST /generate`: Generate images from text prompts
  - Body: `{ "prompt": string, "negative_prompt": string?, "num_inference_steps": number?, "guidance_scale": number? }`
  - Returns: `{ "status": "success", "image": "base64_encoded_image" }`

- `POST /edit`: Edit images using text prompts
  - Body: FormData with `file`, `prompt`, `strength`, `num_inference_steps`, `guidance_scale`, `negative_prompt`
  - Returns: `{ "status": "success", "image": "base64_encoded_image" }`

- `GET /health`: Health check endpoint
  - Returns: `{ "status": "healthy", "models_loaded": boolean }`

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

### Frontend Container
- **Base**: Node.js 20 slim
- **Build**: Production-optimized Next.js build
- **Port**: 3000

### Docker Compose
- **GPU Access**: Automatic GPU passthrough to backend
- **Service Dependencies**: Frontend waits for backend to be ready
- **Environment**: Automatic service discovery between containers

## 🔍 Development Notes

- **GPU Memory**: The application automatically detects CUDA availability and optimizes memory usage
- **Model Loading**: Stable Diffusion models are loaded on startup (may take time on first run)
- **CORS**: Currently configured for development (allows all origins)
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Image Format**: All images are processed as PNG format for consistency

## 🚨 Production Considerations

- Configure CORS properly for production domains
- Set up proper GPU resource limits
- Consider model caching strategies for better performance
- Implement proper logging and monitoring
- Add authentication/authorization if needed
- Optimize Docker images for production deployment

## 📝 License

This is a toy project for educational purposes. Please check individual library licenses for commercial use.

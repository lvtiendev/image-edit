# AGENTS.md - Image Edit Project

## PROJECT METADATA
- **Project Type**: Full-stack AI image generation/editing application
- **Architecture**: Microservices (FastAPI backend + Next.js frontend)
- **Primary Language**: Python (backend), TypeScript (frontend)
- **AI/ML Stack**: Stable Diffusion 2.1, Diffusers, PyTorch
- **Containerization**: Docker + Docker Compose
- **GPU Support**: NVIDIA CUDA (optional but recommended)

## QUICK START COMMANDS
```bash
# Full stack with Docker
docker-compose up --build

# Backend only (Python)
cd server && uv sync && uv run uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Frontend only (Node.js)
cd webapp && yarn install && NEXT_PUBLIC_IMAGE_SERVER_URL=http://localhost:8000 yarn dev
```

## PROJECT STRUCTURE
```
image-edit/
├── server/                    # Python FastAPI backend
│   ├── server.py             # Main API server (140 lines)
│   ├── client_generate.py    # Image generation client (27 lines)
│   ├── client_edit.py        # Image editing client (28 lines)
│   ├── pyproject.toml        # Python dependencies
│   └── Dockerfile            # Backend container
├── webapp/                   # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main app component (67 lines)
│   │   │   └── layout.tsx    # App layout
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx # Chat interface (142 lines)
│   │   │   ├── ImagePanel.tsx# Image display/upload
│   │   │   ├── HistoryPanel.tsx # Image history (44 lines)
│   │   │   └── ui/           # Reusable UI components
│   │   ├── lib/utils.ts      # Utility functions
│   │   └── types/index.ts    # TypeScript definitions
│   ├── package.json          # Node.js dependencies
│   └── Dockerfile            # Frontend container
└── docker-compose.yml        # Multi-service orchestration
```

## KEY FILES TO MODIFY

### Backend (Python/FastAPI)
- **`server/server.py`**: Main API server with endpoints `/generate`, `/edit`, `/health`
- **`server/pyproject.toml`**: Dependencies (FastAPI, Diffusers, PyTorch, etc.)
- **`server/Dockerfile`**: Container configuration with CUDA support

### Frontend (Next.js/React)
- **`webapp/src/app/page.tsx`**: Main application component
- **`webapp/src/components/ChatPanel.tsx`**: Chat interface and API calls
- **`webapp/src/components/ImagePanel.tsx`**: Image display and upload
- **`webapp/src/components/HistoryPanel.tsx`**: Image history management
- **`webapp/package.json`**: Dependencies (Next.js, React, Tailwind, etc.)

## API ENDPOINTS

### Backend API (Port 8000)
```python
# Generate image from text
POST /generate
{
  "prompt": "string",
  "negative_prompt": "string?",
  "num_inference_steps": "number?",
  "guidance_scale": "number?"
}
Response: {"status": "success", "image": "base64_string"}

# Edit existing image
POST /edit
FormData: {
  "file": "image_file",
  "prompt": "string",
  "strength": "number",
  "num_inference_steps": "number",
  "guidance_scale": "number",
  "negative_prompt": "string?"
}
Response: {"status": "success", "image": "base64_string"}

# Health check
GET /health
Response: {"status": "healthy", "models_loaded": boolean}
```

## DEPENDENCIES

### Backend (Python)
```toml
dependencies = [
    "accelerate>=1.2.1",      # GPU acceleration
    "diffusers>=0.32.1",      # Stable Diffusion pipelines
    "fastapi>=0.115.6",       # Web framework
    "pillow>=11.0.0",         # Image processing
    "python-multipart>=0.0.20", # File uploads
    "torch>=2.5.1",           # PyTorch
    "transformers>=4.47.1",   # Hugging Face transformers
    "uvicorn>=0.34.0",        # ASGI server
]
```

### Frontend (Node.js)
```json
{
  "dependencies": {
    "@radix-ui/react-scroll-area": "^1.2.2",
    "@radix-ui/react-slot": "^1.1.1",
    "ai": "^4.0.22",                    // AI SDK for chat
    "class-variance-authority": "^0.7.1",
    "lucide-react": "^0.469.0",         // Icons
    "next": "15.1.3",                   // Next.js framework
    "react": "^19.0.0",                 // React
    "react-dom": "^19.0.0",
    "tailwind-merge": "^2.6.0",
    "zod": "^3.24.1"                    // Validation
  }
}
```

## ENVIRONMENT VARIABLES

### Backend
- No specific environment variables required
- Automatically detects CUDA availability
- Uses default Stable Diffusion 2.1 model

### Frontend
- `NEXT_PUBLIC_IMAGE_SERVER_URL`: Backend server URL (default: http://localhost:8000)

## DOCKER CONFIGURATION

### Backend Container
- **Base**: `nvidia/cuda:12.0.0-base-ubuntu22.04`
- **Package Manager**: UV (modern Python package manager)
- **GPU**: Automatic CUDA detection and optimization
- **Memory**: Attention slicing enabled for GPU memory efficiency

### Frontend Container
- **Base**: `node:20-slim`
- **Package Manager**: Yarn
- **Build**: Production-optimized Next.js build

### Docker Compose
- **GPU Access**: Automatic GPU passthrough to backend
- **Service Dependencies**: Frontend depends on backend
- **Ports**: Frontend (3000), Backend (8000)

## DEVELOPMENT WORKFLOW

### Adding New Features
1. **Backend API**: Modify `server/server.py` for new endpoints
2. **Frontend UI**: Update components in `webapp/src/components/`
3. **Types**: Update `webapp/src/types/index.ts` for new data structures
4. **Styling**: Use Tailwind CSS classes in components

### Common Modifications
- **New API endpoints**: Add to `server/server.py` with proper error handling
- **UI components**: Create in `webapp/src/components/` with TypeScript interfaces
- **Styling**: Use Tailwind CSS utility classes
- **State management**: React hooks in components (no external state management)

## CRITICAL PATTERNS

### Image Handling
- All images are base64 encoded for transmission
- Backend processes images as PIL Image objects
- Frontend converts base64 to Blob for file uploads

### Error Handling
- Backend: FastAPI HTTPException with proper status codes
- Frontend: Try-catch blocks with user-friendly error messages
- API calls include proper error handling and loading states

### Chat Interface
- Uses `ai/react` hook for chat state management
- Commands: `generate:` prefix for image generation, plain text for editing
- Real-time feedback with loading states

## TESTING APPROACH
- **Backend**: Test API endpoints with curl or Postman
- **Frontend**: Manual testing through browser interface
- **Integration**: Full Docker Compose setup for end-to-end testing

## PERFORMANCE CONSIDERATIONS
- **GPU Memory**: Automatic CUDA detection and memory optimization
- **Model Loading**: Models loaded once on startup (slow first run)
- **Image Processing**: Base64 encoding/decoding for all images
- **Memory**: Attention slicing enabled for GPU efficiency

## SECURITY NOTES
- **CORS**: Currently allows all origins (development only)
- **File Uploads**: No file type validation (add if needed)
- **API Keys**: No authentication required (add if needed)

## COMMON ISSUES
1. **GPU Not Detected**: Check NVIDIA Docker runtime installation
2. **Model Loading Slow**: First run downloads models (~4GB)
3. **Memory Issues**: Reduce batch size or enable attention slicing
4. **CORS Errors**: Check `NEXT_PUBLIC_IMAGE_SERVER_URL` environment variable

## EXTENSION POINTS
- **New AI Models**: Modify model loading in `server.py` init_models()
- **Additional Endpoints**: Add new routes in `server.py`
- **UI Components**: Create new components in `webapp/src/components/`
- **Styling**: Modify Tailwind classes or add custom CSS
- **State Management**: Add Redux/Zustand if needed for complex state

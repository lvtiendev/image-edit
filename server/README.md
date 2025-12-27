# Image Edit Server

A FastAPI server for image generation and editing using either Stable Diffusion or Flux models.

## Features

- **Text-to-Image Generation**: Generate images from text prompts
- **Image-to-Image Editing**: Edit existing images with text prompts
- **Model Selection**: Choose between Stable Diffusion 2.1 or FLUX.1 Dev at startup
- **Memory Efficient**: Only loads one model at a time to conserve memory

## Model Selection

The server supports two models, but only one can be loaded at a time due to memory constraints:

- **Stable Diffusion 2.1**: Supports negative prompts, good for general use
- **FLUX.1 Dev**: Higher quality output, but doesn't support negative prompts

## Usage

### Starting the Server

#### Method 1: Command Line Argument
```bash
# Start with Stable Diffusion (default)
python server.py

# Start with Stable Diffusion explicitly
python server.py stable-diffusion

# Start with Flux
python server.py flux
```

#### Method 2: Environment Variable
```bash
# Set environment variable
export MODEL_TYPE=flux
python server.py

# Or inline
MODEL_TYPE=flux python server.py
```

### API Endpoints

#### Health Check
```bash
GET /health
```
Returns server status and current model information.

#### Get Model Information
```bash
GET /models
```
Returns information about the currently loaded model.

#### Generate Image
```bash
POST /generate
Content-Type: application/json

{
  "prompt": "a beautiful landscape",
  "negative_prompt": "blurry, low quality",  // Only for Stable Diffusion
  "num_inference_steps": 50,
  "guidance_scale": 7.5
}
```

#### Edit Image
```bash
POST /edit
Content-Type: multipart/form-data

- file: [image file]
- prompt: "make it more colorful"
- strength: 0.75
- num_inference_steps: 50
- guidance_scale: 7.5
- negative_prompt: "blurry"  // Only for Stable Diffusion
```

## Model-Specific Notes

### Stable Diffusion 2.1
- Supports negative prompts
- Good balance of speed and quality
- Lower memory usage
- Default model

### FLUX.1 Dev
- Higher quality output
- Does not support negative prompts
- Higher memory usage
- Requires more VRAM/GPU memory

## Requirements

- Python 3.10+
- CUDA-compatible GPU (recommended)
- Sufficient VRAM for the selected model:
  - Stable Diffusion: ~4GB VRAM
  - FLUX: ~8GB+ VRAM

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
# or
uv sync
```

## Docker Usage

### Using Docker Compose (Recommended)

#### With Stable Diffusion (default):
```bash
# Start with Stable Diffusion
docker-compose up --build

# Or explicitly
docker-compose -f docker-compose.yml up --build
```

#### With Flux:
```bash
# Start with Flux model
docker-compose -f docker-compose.flux.yml up --build

# Or using override file
cp docker-compose.override.yml.example docker-compose.override.yml
# Edit docker-compose.override.yml to set MODEL_TYPE=flux
docker-compose up --build
```

### Using Docker directly

```bash
# Build the image
docker build -t image-edit-server ./server

# Run with Stable Diffusion (default)
docker run -p 8000:8000 --gpus all image-edit-server

# Run with Flux
docker run -p 8000:8000 --gpus all -e MODEL_TYPE=flux image-edit-server

# Run with custom model selection
docker run -p 8000:8000 --gpus all -e MODEL_TYPE=stable-diffusion image-edit-server
```

### Environment Variables

- `MODEL_TYPE`: Set to `stable-diffusion` or `flux` (default: `stable-diffusion`)
- `NVIDIA_VISIBLE_DEVICES`: Set to `all` for GPU access (handled by docker-compose)

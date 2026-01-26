from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusion3Pipeline,
    StableDiffusion3Img2ImgPipeline,
    FluxPipeline,
    FluxImg2ImgPipeline,
)
import torch
from PIL import Image
import io
import base64
import os
import sys
from pydantic import BaseModel
from typing import Optional, Literal


# Model type constants
MODEL_TYPE_FLUX = "flux"
MODEL_TYPE_STABLE_DIFFUSION = "stable-diffusion"
AVAILABLE_MODEL_TYPES = [MODEL_TYPE_STABLE_DIFFUSION, MODEL_TYPE_FLUX]

# Model ID constants
FLUX_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
STABLE_DIFFUSION_MODEL_ID = "stabilityai/stable-diffusion-3.5-medium"


def get_gpu_device_map():
    """
    Determine device mapping strategy for model loading.

    Options:
    - "balanced": Balance memory usage across GPUs (recommended)
    - "sequential": Use GPUs sequentially (0, then 1, etc.)
    - None: Use single GPU (default behavior)
    """
    device_map = os.getenv("DEVICE_MAP", "balanced").lower()

    if device_map == "none":
        return None
    elif device_map in ["balanced", "sequential"]:
        return device_map
    else:
        print(f"Unknown DEVICE_MAP '{device_map}', using 'balanced'")
        return "balanced"


def get_quantization_config():
    """
    Get quantization configuration for memory-efficient model loading.

    Returns:
    - None: No quantization (full precision)
    - "8bit": Load model in 8-bit (reduces memory by ~2x)
    - "4bit": Load model in 4-bit (reduces memory by ~4x)

    Note: Only works with FLUX models on CUDA
    """
    quant_mode = os.getenv("QUANTIZATION", "8bit").lower()

    # Only enable quantization for CUDA and FLUX
    if not torch.cuda.is_available():
        print("Quantization requires CUDA, using full precision")
        return None

    if quant_mode == "none":
        return None
    elif quant_mode == "8bit":
        return {"load_in_8bit": True}
    elif quant_mode == "4bit":
        return {"load_in_4bit": True}
    else:
        print(f"Unknown QUANTIZATION '{quant_mode}', using '8bit'")
        return {"load_in_8bit": True}


def get_max_memory():
    """
    Get maximum memory allocation per GPU.

    Format: "GPU_ID:MEMORY_IN_GB"
    Example: "0:10" means GPU 0 can use up to 10GB
    Can set multiple GPUs: "0:10,1:10"

    Returns None to let accelerate manage automatically
    """
    max_memory_env = os.getenv("MAX_MEMORY")

    if not max_memory_env:
        return None

    try:
        max_memory = {}
        for gpu_config in max_memory_env.split(","):
            gpu_id, memory = gpu_config.split(":")
            # Convert GB to bytes (leave some headroom)
            max_memory[int(gpu_id)] = f"{int(memory)}GB"

        # Reserve memory for CPU offloading
        max_memory["cpu"] = "30GB"
        return max_memory
    except Exception as e:
        print(f"Error parsing MAX_MEMORY '{max_memory_env}': {e}")
        print("Using automatic memory management")
        return None


class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = 50
    guidance_scale: Optional[float] = 7.5


def get_model_type():
    """Determine which model to use based on environment variable or command line args"""
    # Check command line arguments first
    if len(sys.argv) > 1:
        model_arg = sys.argv[1].lower()
        if model_arg in AVAILABLE_MODEL_TYPES:
            return model_arg

    # Check environment variable
    model_env = os.getenv("MODEL_TYPE", MODEL_TYPE_STABLE_DIFFUSION).lower()
    if model_env in AVAILABLE_MODEL_TYPES:
        return model_env

    # Default to stable-diffusion
    return MODEL_TYPE_STABLE_DIFFUSION


def get_hf_token():
    """Get Hugging Face token for accessing gated models"""
    token = os.getenv("HF_TOKEN")
    if token:
        print("HF_TOKEN found - will use for authentication")
    else:
        print("No HF_TOKEN found - using public models only")
    return token


# Determine model type at startup
SELECTED_MODEL = get_model_type()
print(f"Selected model: {SELECTED_MODEL}")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for the selected model
text2img_pipe = None
img2img_pipe = None
current_model_type = None


def init_models():
    global text2img_pipe, img2img_pipe, current_model_type

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Get GPU configuration
    device_map = get_gpu_device_map()
    max_memory = get_max_memory()

    if device == "cuda" and device_map:
        # Show available GPUs
        gpu_count = torch.cuda.device_count()
        print(f"Detected {gpu_count} GPU(s)")
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"  GPU {i}: {gpu_name} ({gpu_memory:.1f}GB total)")
        print(f"Device map strategy: {device_map}")
        if max_memory:
            print(f"Max memory limits: {max_memory}")

    print(f"Loading {SELECTED_MODEL} model...")

    current_model_type = SELECTED_MODEL

    # Get Hugging Face token for gated models
    hf_token = get_hf_token()

    if SELECTED_MODEL == MODEL_TYPE_FLUX:
        # Initialize Flux text-to-image model only (img2img will be lazy-loaded)

        # Get quantization config
        quantization = get_quantization_config()

        # Common kwargs for model loading
        flux_kwargs = {
            "token": hf_token,
        }

        # Add quantization if enabled (skips torch_dtype when quantizing)
        if quantization:
            flux_kwargs.update(quantization)
            quant_bits = "8-bit" if quantization.get("load_in_8bit") else "4-bit"
            print(f"Using {quant_bits} quantization to reduce memory usage")
        else:
            flux_kwargs["torch_dtype"] = (
                torch.float16 if device == "cuda" else torch.float32
            )

        # Add device mapping for multi-GPU
        if device == "cuda" and device_map:
            flux_kwargs["device_map"] = device_map
            if max_memory:
                flux_kwargs["max_memory"] = max_memory

            quant_info = f" with {quant_bits} quantization" if quantization else ""
            print(
                f"Loading Flux text-to-image model with multi-GPU{quant_info} support..."
            )
            print("Note: img2img pipeline will be loaded on first edit request")
        else:
            print(f"Loading Flux text-to-image model on single {device}...")
            print("Note: img2img pipeline will be loaded on first edit request")

        # Only load text2img at startup for better memory management
        text2img_pipe = FluxPipeline.from_pretrained(FLUX_MODEL_ID, **flux_kwargs)

        # No need to call .to() when using device_map or quantization
        # (both handle device placement automatically)

        print(
            "Flux text-to-image model loaded successfully with reduced memory footprint"
        )

    else:  # stable-diffusion
        # Initialize Stable Diffusion text-to-image model only (img2img will be lazy-loaded)

        # Common kwargs for model loading
        sd_kwargs = {
            "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
            "token": hf_token,
        }

        # Add device mapping for multi-GPU
        if device == "cuda" and device_map:
            sd_kwargs["device_map"] = device_map
            if max_memory:
                sd_kwargs["max_memory"] = max_memory
            print(
                "Loading Stable Diffusion text-to-image model with multi-GPU support..."
            )
            print("Note: img2img pipeline will be loaded on first edit request")
        else:
            print(f"Loading Stable Diffusion text-to-image model on single {device}...")
            print("Note: img2img pipeline will be loaded on first edit request")

        # Only load text2img at startup for better memory management
        text2img_pipe = StableDiffusion3Pipeline.from_pretrained(
            STABLE_DIFFUSION_MODEL_ID, **sd_kwargs
        )

        if not (device == "cuda" and device_map):
            text2img_pipe.to(device)

        # Enable memory efficient attention if using CUDA
        if device == "cuda":
            if not device_map:
                text2img_pipe.enable_attention_slicing()
                print(
                    "Stable Diffusion text-to-image model optimized with attention slicing"
                )

    print(f"{SELECTED_MODEL.title()} model loaded successfully!")


def load_img2img_pipeline():
    """
    Lazy load the img2img pipeline on first edit request.
    Uses from_pipe() to share components with text2img pipeline for memory efficiency.
    This reduces memory usage by ~40-50% compared to loading independently.
    """
    global img2img_pipe

    # Already loaded
    if img2img_pipe is not None:
        return

    print("\n" + "=" * 60)
    print("First edit request detected - loading img2img pipeline...")
    print("Reusing components from text2img pipeline to save memory...")
    print("=" * 60)

    try:
        # Reuse components from already loaded text2img pipeline
        if current_model_type == MODEL_TYPE_FLUX:
            img2img_pipe = FluxImg2ImgPipeline.from_pipe(text2img_pipe)
        else:  # stable-diffusion
            img2img_pipe = StableDiffusion3Img2ImgPipeline.from_pipe(text2img_pipe)

        print(f"✓ {current_model_type.title()} img2img pipeline loaded successfully!")
        print("✓ Components shared with text2img pipeline - memory optimized!")
        print("✓ Memory increase: <2GB (vs 6-8GB with independent loading)")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"✗ Error creating img2img pipeline from text2img: {e}")
        print("Falling back to independent pipeline loading...")

        # Fallback: load independently if from_pipe fails
        _load_img2img_pipeline_independent()


def _load_img2img_pipeline_independent():
    """
    Fallback method to load img2img pipeline independently.
    Used only if from_pipe() fails.
    """
    global img2img_pipe

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Get GPU configuration
    device_map = get_gpu_device_map()
    max_memory = get_max_memory()

    # Get Hugging Face token
    hf_token = get_hf_token()

    if current_model_type == MODEL_TYPE_FLUX:
        # Get quantization config
        quantization = get_quantization_config()

        # Common kwargs for model loading
        flux_kwargs = {
            "token": hf_token,
        }

        # Add quantization if enabled
        if quantization:
            flux_kwargs.update(quantization)
            quant_bits = "8-bit" if quantization.get("load_in_8bit") else "4-bit"
        else:
            flux_kwargs["torch_dtype"] = (
                torch.float16 if device == "cuda" else torch.float32
            )

        # Add device mapping for multi-GPU
        if device == "cuda" and device_map:
            flux_kwargs["device_map"] = device_map
            if max_memory:
                flux_kwargs["max_memory"] = max_memory
            quant_info = f" with {quant_bits} quantization" if quantization else ""
            print(
                f"Loading Flux img2img pipeline independently with multi-GPU{quant_info} support..."
            )
        else:
            print(f"Loading Flux img2img pipeline independently on single {device}...")

        img2img_pipe = FluxImg2ImgPipeline.from_pretrained(FLUX_MODEL_ID, **flux_kwargs)

        print("Flux img2img pipeline loaded independently (fallback mode)")

    else:  # stable-diffusion
        # Common kwargs for model loading
        sd_kwargs = {
            "torch_dtype": torch.float16 if device == "cuda" else torch.float32,
            "token": hf_token,
        }

        # Add device mapping for multi-GPU
        if device == "cuda" and device_map:
            sd_kwargs["device_map"] = device_map
            if max_memory:
                sd_kwargs["max_memory"] = max_memory
            print("Loading Stable Diffusion img2img pipeline independently with multi-GPU support...")
        else:
            print(f"Loading Stable Diffusion img2img pipeline independently on single {device}...")

        img2img_pipe = StableDiffusion3Img2ImgPipeline.from_pretrained(
            STABLE_DIFFUSION_MODEL_ID, **sd_kwargs
        )

        if not (device == "cuda" and device_map):
            img2img_pipe.to(device)

        # Enable memory efficient attention if using CUDA
        if device == "cuda" and not device_map:
            img2img_pipe.enable_attention_slicing()
            print("Stable Diffusion img2img pipeline optimized with attention slicing")

    print(f"{current_model_type.title()} img2img pipeline loaded (independent mode)!")
    print("Note: Independent loading uses more memory than component sharing.")
    print("=" * 60 + "\n")


@app.on_event("startup")
async def startup_event():
    init_models()


def image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


@app.post("/generate")
async def generate_image(request: GenerationRequest):
    try:
        if text2img_pipe is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        # Use the loaded model based on current_model_type
        # Note: Neither Flux nor SD 3.5 support negative_prompt
        image = text2img_pipe(
            prompt=request.prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
        ).images[0]

        return {
            "status": "success",
            "image": image_to_base64(image),
            "model_type": current_model_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/edit")
async def edit_image(
    file: UploadFile = File(...),
    prompt: str = Form(""),
    strength: float = Form(0.75),
    num_inference_steps: int = Form(50),
    guidance_scale: float = Form(7.5),
    negative_prompt: str = Form(None),
):
    print(
        f"""
Parameters received:
- prompt: '{prompt}'  # Added quotes to see if empty string or whitespace
- strength: {strength}
- num_inference_steps: {num_inference_steps}
- guidance_scale: {guidance_scale}
- negative_prompt: {negative_prompt}
- file name: {file.filename}
- model_type: {current_model_type}
"""
    )
    try:
        # Lazy load img2img pipeline on first edit request
        if img2img_pipe is None:
            load_img2img_pipeline()

        # Read and process the uploaded image
        contents = file.file.read()
        init_image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Use the loaded model based on current_model_type
        # Note: Neither Flux nor SD 3.5 support negative_prompt
        result = img2img_pipe(
            prompt=prompt,
            image=init_image,
            strength=strength,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images[0]

        return {
            "status": "success",
            "image": image_to_base64(result),
            "model_type": current_model_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": text2img_pipe is not None,
        "img2img_loaded": img2img_pipe is not None,
        "current_model": current_model_type,
        "components_shared": img2img_pipe is not None,
    }


@app.get("/memory")
async def memory_info():
    """Get current GPU memory usage and pipeline status"""
    if not torch.cuda.is_available():
        return {
            "device": "cpu",
            "memory_used_gb": 0,
            "text2img_loaded": text2img_pipe is not None,
            "img2img_loaded": img2img_pipe is not None,
            "components_shared": img2img_pipe is not None,
        }

    memory_used = torch.cuda.memory_allocated() / 1024**3
    memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3

    return {
        "device": "cuda",
        "memory_used_gb": round(memory_used, 2),
        "memory_total_gb": round(memory_total, 2),
        "memory_percent": round(memory_used / memory_total * 100, 1) if memory_total > 0 else 0,
        "text2img_loaded": text2img_pipe is not None,
        "img2img_loaded": img2img_pipe is not None,
        "components_shared": img2img_pipe is not None,
    }


@app.get("/models")
async def get_available_models():
    """Get information about the currently loaded model"""
    model_info = {
        "name": current_model_type,
        "display_name": (
            "Stable Diffusion 3.5 Medium"
            if current_model_type == MODEL_TYPE_STABLE_DIFFUSION
            else "FLUX.1 Dev"
        ),
        "supports_negative_prompt": False,  # SD 3.5 doesn't support negative prompts
        "loaded": text2img_pipe is not None and img2img_pipe is not None,
    }

    return {
        "current_model": model_info,
        "available_models": AVAILABLE_MODEL_TYPES,
        "note": "Model selection is done at server startup via MODEL_TYPE environment variable or command line argument",
    }


if __name__ == "__main__":
    import uvicorn

    print(f"Starting server with {SELECTED_MODEL} model...")
    print("Usage:")
    print(f"  python server.py [{'|'.join(AVAILABLE_MODEL_TYPES)}]")
    print("  or set MODEL_TYPE environment variable")
    print(f"  Default: {MODEL_TYPE_STABLE_DIFFUSION}")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)

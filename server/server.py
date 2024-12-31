from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import io
import base64
from pydantic import BaseModel
from typing import Optional


class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = 50
    guidance_scale: Optional[float] = 7.5


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
text2img_pipe = None
img2img_pipe = None


def init_models():
    global text2img_pipe, img2img_pipe

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model_id = "stabilityai/stable-diffusion-2-1"
    text2img_pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    text2img_pipe.to(device)

    # Initialize img2img pipeline
    img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    img2img_pipe.to(device)

    # Enable memory efficient attention if using CUDA
    if device == "cuda":
        text2img_pipe.enable_attention_slicing()
        img2img_pipe.enable_attention_slicing()


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
        image = text2img_pipe(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
        ).images[0]

        return {"status": "success", "image": image_to_base64(image)}
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
"""
    )
    try:
        # Read and process the uploaded image
        contents = file.file.read()
        init_image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Generate the edited image
        result = img2img_pipe(
            prompt=prompt,
            image=init_image,
            negative_prompt=negative_prompt,
            strength=strength,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        ).images[0]

        return {"status": "success", "image": image_to_base64(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": text2img_pipe is not None and img2img_pipe is not None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

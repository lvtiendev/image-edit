import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "A beautiful sunset over mountains",
        "negative_prompt": "blur, distortion",
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
    },
)

if response.status_code == 200:
    # Get the base64 encoded image from the response
    image_data = response.json()["image"]

    # Decode and save the image
    import base64

    image_bytes = base64.b64decode(image_data)
    with open("generated_image.png", "wb") as f:
        f.write(image_bytes)
    print("Image saved as generated_image.png")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

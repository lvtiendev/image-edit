import requests

url = "http://localhost:8000/edit"

with open("generated_image.png", "rb") as f:
    files = {"file": f}
    params = {
        "prompt": "Add snow weather",
        "strength": 0.75,
    }
    print("Sending request with params:", params)
    response = requests.post(url, files=files, data=params)

if response.status_code == 200:
    # Get the base64 encoded image from the response
    image_data = response.json()["image"]

    # Decode and save the image
    import base64

    image_bytes = base64.b64decode(image_data)
    with open("edited_image.png", "wb") as f:
        f.write(image_bytes)
    print("Image saved as edited_image.png")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

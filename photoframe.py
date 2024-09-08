from io import BytesIO
import logging
from PIL import Image
import time
import base64
import requests
import os
import random

# Function to convert a PIL image to a Base64 encoded string
def pil_image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def send_image(file):
    im = Image.open(file)
    width, height = im.size
    print("Original width: " + str(width) + ", Height: " + str(height))
    if (width > height):
        ratio = height/width
        width = 480
        height = int(ratio*320)
    elif (height == width):
        height = 320
        width = 480
    else:
        ratio = width/height
        height = 320
        width = int(ratio*480)
    print("Width: " + str(width) + ", Height: " + str(height))

    scaled = im.resize((width, height))
    background = Image.new('RGB', (480, 320), (0, 0, 0)) 
    left = (480 - width) // 2
    top = (320 - height) // 2
    print("Left: " + str(left) + ", Top: " + str(top))
    background.paste(scaled, (left, top))
    base64_image = pil_image_to_base64(background)
    url = 'http://127.0.0.1:5000/upload'  # Change this if you are using FastAPI
    payload = {'image': base64_image}
    response = requests.post(url, json=payload)
    print(response)

def pick_random_png(directory):
     # List all files in the directory
    files = os.listdir(directory)
    
    # Filter out the files that have a .png extension
    png_files = [f for f in files if f.lower().endswith('.png')]
    
    if not png_files:
        print("No PNG files found in the directory.")
        return None
    
    # Randomly pick one PNG file
    chosen_file = random.choice(png_files)
    
    return chosen_file

dir = "/home/mattg/dev/ComfyUI/output/"
while True:
    img = pick_random_png(directory = dir)
    send_image(dir + img)
    time.sleep(5)

import feedparser
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time
import base64
import requests
from io import BytesIO


def pil_image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def send_image(im):
    width_percent = 480 / float(im.size[0])
    new_height = max(int((float(im.size[1]) * float(width_percent))), 320)
    print("Width: " + str(width_percent) + ", Height: " + str(new_height))
    scaled = im.resize((480, new_height))
    base64_image = pil_image_to_base64(scaled)
    url = 'http://127.0.0.1:5000/upload'  # Change this if you are using FastAPI
    payload = {'image': base64_image}
    response = requests.post(url, json=payload)

def create_image(title, text):
    # Define image size and background color
    width, height = 480, 320
    background_color = (0, 0, 0)  # Black
    white = (255, 255, 255)  # White
    blue = (100, 100, 255)  # Blue
    
    # Create a new image with a black background
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Load a font
    try:
        font = ImageFont.truetype("OpenSans-Bold.ttf", 18)  # Ensure 'arial.ttf' is available
    except IOError:
        font = ImageFont.load_default()
    # Wrap text to fit within the image width
    title_wrapped = textwrap.fill(title, width=50)
    # Draw text on the image
    draw.text((10, 10), title_wrapped, fill=blue, font=font)
    text_wrapped = textwrap.fill(text, width=50)
    draw.text((10, 100), text_wrapped, fill=white, font=font)
    send_image(image)
    time.sleep(15)

def fetch_rss_feed(url):
    # Parse the RSS feed
    feed = feedparser.parse(url)
    
    # Check if the feed has entries
    if not feed.entries:
        print("No entries found.")
        return
    
    # Iterate through the entries
    for i, entry in enumerate(feed.entries):
        title = entry.get("title", "No Title")
        summary = entry.get("summary", "No Summary")
        content = f"Title: {title}\nSummary: {summary}"
        
        # Create an image for each article
        create_image(f"NYT\n{feed.feed.get('published', 'No Date')}\nTitle: {title}", summary)

if __name__ == "__main__":

    rss_url = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    while True:
        fetch_rss_feed(rss_url)


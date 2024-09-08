from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import base64
import requests
import yaml

from PIL import Image
from io import BytesIO

import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome (no GUI)
chrome_options.add_argument("--disable-gpu")

chrome_options.add_argument("--window-size=1440x960")  # Set window size to ensure proper rendering

# Path to your chromedriver executable
chromedriver_path = "/path/to/chromedriver"

# Set up the WebDriver
#service = ChromeService(executable_path=chromedriver_path)
service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

with open('grafana-config.yaml', 'r') as file:
    config = yaml.safe_load(file)

grafana = config['grafana']
grafana_url = grafana['url']
username = grafana['username']
password = grafana['password']
ax206_url = config['ax206']['url']
dashboards = grafana['dashboards']

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
    url = ax206_url  # Change this if you are using FastAPI
    payload = {'image': base64_image}
    response = requests.post(url, json=payload)

def login():
    login_url = grafana_url + "/login"
    driver.get(login_url)
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "user")))
    password_field = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')

    # Enter your credentials
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click the login button
    login_button.click()

    # Wait for the dashboard page to load
    #wait.until(EC.url_contains("/d/"))
    time.sleep(1)

def send_dashboard(grafana_url, crop_top):
    # Open the Grafana dashboard URL
    driver.get(grafana_url)

    # Optionally wait for the dashboard to fully load
    time.sleep(1)  # Adjust the sleep time as needed

    # Take a screenshot
    # Load the screenshot into a Pillow Image object
    binary = driver.get_screenshot_as_png()
    im = Image.open(BytesIO(binary))
    width, height = im.size
    crop_im = im.crop((0, crop_top, width, height))
    scaled_image = crop_im.resize((480, 320))
    send_image(scaled_image)
    time.sleep(5)

send_image(Image.open("loading.png"))
login()

while True:
    crop_top = 130
    for dashboard in dashboards:
        if ('path' in dashboard):
            if ('crop_top' in dashboard):
                crop_top = dashboard['crop_top']
            else:
                crop_top = 130
            send_dashboard(grafana_url + dashboard['path'], crop_top)
            time.sleep(5)

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import os  # Added missing import
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)

# ... [keep USER_AGENTS and get_enhanced_headers() the same] ...

def setup_selenium():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    
    # Use webdriver-manager with custom Chrome path
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def scrape_with_selenium(url):
    driver = setup_selenium()
    try:
        driver.get(url)
        time.sleep(random.uniform(1, 3))  # FIXED THIS LINE
        
        # Simulate human-like scrolling
        scroll_script = """
            window.scrollTo({
                top: document.body.scrollHeight * 0.3,
                behavior: 'smooth'
            });
        """
        driver.execute_script(scroll_script)
        time.sleep(random.uniform(0.5, 1.5))
        
        return driver.page_source
    except Exception as e:
        raise e
    finally:
        driver.quit()

# ... [rest of the code remains the same] ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # this is the code

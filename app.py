from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
CORS(app)

# Configure retry strategy with backoff
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)

# Common headers list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
]

PROXIES = {  # Add your proxy servers here
    # "http": "http://user:pass@ip:port",
    # "https": "http://user:pass@ip:port"
}

def get_enhanced_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": str(random.randint(0, 1)),
        "Connection": "keep-alive"
    }

@app.route('/', methods=['POST'])
def run_script():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        # Add random delay to mimic human behavior
        time.sleep(random.uniform(0.5, 2.5))

        response = session.get(
            url,
            headers=get_enhanced_headers(),
            proxies=PROXIES,
            timeout=15
        )
        response.raise_for_status()

        # Handle potential JavaScript rendering
        if "text/html" not in response.headers.get('Content-Type', ''):
            return jsonify({"error": "Non-HTML content received"}), 400

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "meta", "link"]):
            element.decompose()

        text = ' '.join(soup.stripped_strings)

        # Enhanced email regex pattern
        email_pattern = r'\b[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,64}@(?:[a-zA-Z0-9-]{1,63}\.){1,8}[a-zA-Z]{2,63}\b'
        emails = re.findall(email_pattern, text)
        emails = list(set(emails))  # Remove duplicates

        return jsonify({
            "status": "success",
            "count": len(emails),
            "emails": emails
        })

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 403:
            return jsonify({
                "error": "Access forbidden (403)",
                "message": "Website has strong bot protection"
            }), 403
        return jsonify({"error": f"HTTP Error {status_code}"}), status_code

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timeout"}), 504

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
import os
import requests
from bs4 import BeautifulSoup

from helpers import format_url

CACHE_DIR = "cache"

def get_passage(version_id, book_code, chapter):
    fname = f"{version_id}.{book_code}.{chapter}.html"
    yvReader = None
    if fname in os.listdir(CACHE_DIR):
        print(f"Loading {fname} from cache.")
        with open(os.path.join(CACHE_DIR, fname), "r") as f:
            yvReader = BeautifulSoup(f.read())
    else:
        url = format_url(version_id, book_code, chapter)
        print(f"Loading from {url}")
        response = requests.get(url)
        page = response.content
        soup = BeautifulSoup(page)
        yvReader = soup.find("div", class_=re.compile("ChapterContent_yv-bible-text"))

        # Save to cache
        with open(os.path.join(CACHE_DIR, fname), "w", encoding="utf-8") as f:
            f.write(str(yvReader))
    
    return yvReader
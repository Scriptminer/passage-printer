import os
import requests
from bs4 import BeautifulSoup

CACHE_DIR = "cache"
URL_PATTERN = "https://www.bible.com/bible/{version_id}/{book_code}.{chapter}"

def resolve_version(version_name):
    if type(version_name) == int:
        return version_name
    language_info = [None, "", None]
    with open("custom_version_info.txt") as f:
        for line in f.readlines():
            parts = line.strip().split(";")
            if version_name.lower() in parts[1].lower():
                language_info = parts
    return language_info[0]

def format_url(version_id, book_code,chapter):
    return URL_PATTERN.format(version_id=version_id,book_code=book_code,chapter=chapter)

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
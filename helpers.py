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
    
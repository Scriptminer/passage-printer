import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.bible.com/bible/{version_id}/{book_code}.{chapter}"

response = requests.get(URL.format(version_id="113",book_code="PHP",chapter=2))
page = response.content

soup = BeautifulSoup(page)

chapter = soup.find("div", class_=re.compile("ChapterContent_chapter"))

formats = {
    "chapter_heading": "# {content}\n", # Heading of Chapter
    "s1": "## {content}", # Section heading
    "p": "{content}\n", # Paragraph
    "q1": "    {content}\n", # Indented quote
    "q2": "       {content}\n", # Double indented quote
    "qa": "*{content}*\n", # Quote heading (e.g., section titles in Psalm 119)
    "b": "\n", # Blank line
    "d": "", # Description, as in the Psalms

    "wj": "<span color='red'>{content}</span>", # Words of Jesus
    "label": "^{content}^", # Superscript verse label
    "content": "{content}", # Regular Verse contents

    "note_label": "^[{content}]^",
}

markdown_doc = ""

chapter_title = soup.find("div", class_=re.compile("ChapterContent_reader")).find("h1").getText()
markdown_doc += formats["chapter_heading"].format(content=chapter_title)

class Footnotes:
    text_notes = []
    next_note_label = "a"

    def __init__(self):
        pass
    
    def add_note(self, footnote_section):
        footnote = footnote_section.getText()[1:] # Need to extract italics etc in future
        label = self.next_note_label
        self.text_notes.append( (label, footnote) )
        self.update_next_note_label()
        return label
    
    def update_next_note_label(self):
        self.next_note_label = chr(ord(self.next_note_label)+1)
    
    def print_notes(self):
        out = "\n".join([f"{label}: {note}" for label, note in self.text_notes])
        return out

footnotes = Footnotes()

for chapter_section in chapter.find_all(recursive=False):
    section_type = re.findall("^ChapterContent_(.*)__.*$", chapter_section["class"][0])[0]
    print(f"#{section_type}")
    if section_type == "p" or section_type == "q1" or section_type == "q2":
        paragraph_text = ""
        for paragraph_section in chapter_section.find_all(recursive=False):
            paragraph_section_type = re.findall("^ChapterContent_(.*)__.*$", paragraph_section["class"][0])[0]
            print(paragraph_section["class"],",",paragraph_section_type)
            if paragraph_section_type == "verse":
                for verse_section in paragraph_section.find_all(recursive=False):
                    print(f"...",verse_section)
                    verse_section_type = re.findall("^ChapterContent_(.*)__.*$", verse_section["class"][0])[0]
                    if verse_section_type == "note":
                        paragraph_text += formats["note_label"].format(content = footnotes.add_note(verse_section))
                    else:
                        paragraph_text += formats[verse_section_type].format(content = verse_section.getText())
            else:
                print("UNEXPECTED PART OF SECTION")
        markdown_doc += formats[section_type].format(content=paragraph_text)

markdown_doc += "\n" + footnotes.print_notes()

with open("out.md", "w") as f:
    f.write(markdown_doc)
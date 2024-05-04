from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_BREAK, WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Mm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os
import re
import requests
from bs4 import BeautifulSoup

CACHE_DIR = "cache"
URL = "https://www.bible.com/bible/{version_id}/{book_code}.{chapter}"
PAGE_SIZE = {
    "A4": (Mm(210), Mm(297)),
    "A5": (Mm(148), Mm(210)),
}

def set_margin(section, margin):
    section.left_margin, section.right_margin, section.top_margin, section.bottom_margin = [margin]*4

def configure_portrait_parallel(doc):
    """ A4 portrait page with left and right sections """
    section = doc.sections[-1]
    section.page_width, section.page_height = PAGE_SIZE["A4"]
    set_margin(section, Mm(15))
    table = doc.add_table(rows=1, cols=2)
    return table.cell(0,0), table.cell(0,1)

def configure_portrait_singular(doc):
    """ A5 portrait page """
    section = doc.sections[-1]
    section.page_width, section.page_height = PAGE_SIZE["A5"]
    set_margin(section, Mm(15))
    return doc

def configure_landscape_singular(doc):
    """ A5 landscape page """
    section = doc.sections[-1]
    section.page_height, section.page_width = PAGE_SIZE["A5"]
    set_margin(section, Mm(15))
    return doc

def add_styles(document):
    note = document.styles.add_style("note", style_type = WD_STYLE_TYPE.CHARACTER)
    note.font.superscript = True

    label = document.styles.add_style("label", style_type = WD_STYLE_TYPE.CHARACTER)
    label.font.superscript = True

    small_caps = document.styles.add_style("sc", style_type = WD_STYLE_TYPE.CHARACTER)
    small_caps.font.small_caps = True

    paragraph_caps = document.styles.add_style("pc", style_type = WD_STYLE_TYPE.PARAGRAPH)
    paragraph_caps.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_caps.font.small_caps = True

    words_of_Jesus = document.styles.add_style("wj", style_type = WD_STYLE_TYPE.CHARACTER)
    words_of_Jesus.font.color.rgb = RGBColor(255,0,0)

    # Regular content
    document.styles.add_style("content", style_type = WD_STYLE_TYPE.CHARACTER)
    document.styles.add_style("pn", style_type = WD_STYLE_TYPE.CHARACTER)

    heading = document.styles.add_style("heading", style_type = WD_STYLE_TYPE.CHARACTER)
    heading.font.bold = True

    chapter_heading = document.styles.add_style("chapter_heading", style_type = WD_STYLE_TYPE.CHARACTER)
    chapter_heading.font.bold = True
    chapter_heading.font.size = Pt(16)

    # Regular paragraphs
    document.styles.add_style("p", style_type = WD_STYLE_TYPE.PARAGRAPH)
    document.styles.add_style("m", style_type = WD_STYLE_TYPE.PARAGRAPH)

    quote_level_1 = document.styles.add_style("q1", style_type = WD_STYLE_TYPE.PARAGRAPH)
    quote_level_1.paragraph_format.left_indent = Pt(15)
    quote_level_1.paragraph_format.space_after = Pt(0)

    quote_level_2 = document.styles.add_style("q2", style_type = WD_STYLE_TYPE.PARAGRAPH)
    quote_level_2.paragraph_format.left_indent = Pt(30)
    quote_level_2.paragraph_format.space_after = Pt(0)

    quote_level_3 = document.styles.add_style("q3", style_type = WD_STYLE_TYPE.PARAGRAPH)
    quote_level_3.paragraph_format.left_indent = Pt(40)
    quote_level_3.paragraph_format.space_after = Pt(0)

    # Annotations, as in Psalm 119, and section headings
    quote_annotation = document.styles.add_style("qa", style_type = WD_STYLE_TYPE.PARAGRAPH)
    quote_annotation.paragraph_format.space_before = Pt(12)
    quote_annotation.paragraph_format.space_after = Pt(0)

    blank_line = document.styles.add_style("blank_line", style_type = WD_STYLE_TYPE.PARAGRAPH)

    table_vertical_two_column = document.styles.add_style("table_vertical_two_column", style_type = WD_STYLE_TYPE.TABLE)
    table_vertical_two_column

    footnotes = document.styles.add_style("footnotes", style_type = WD_STYLE_TYPE.PARAGRAPH)
    footnotes.font.size = Pt(9)

    copyright = document.styles.add_style("copyright", style_type = WD_STYLE_TYPE.PARAGRAPH)
    copyright.font.size = Pt(9)
    copyright.font.italic = True

def add_verse_section(paragraph, verse_section_data, footnotes_handler, passage_pointer):
    verse_section_type = re.findall("^ChapterContent_([a-zA-Z0-9]*)_*.*$", verse_section_data["class"][0])[0]
    content = verse_section_data.getText()

    if verse_section_type == "label":
        passage_pointer.update_state(content)
    
    if passage_pointer.state != PassagePointer.IN_PASSAGE:
        return
    
    if paragraph["paragraph"] == False:
        add_heading_section(paragraph["doc"], passage_pointer.last_section, passage_pointer) # Add the previous heading
        paragraph["paragraph"] = paragraph["create"](paragraph["doc"])
    
    if verse_section_type == "note":
        content = f"[{footnotes_handler.add_note(verse_section_data)}]"
    
    paragraph["paragraph"].add_run(content, style=verse_section_type)

def add_heading_section(doc, heading_text, passage_pointer):
    if heading_text and passage_pointer.state == PassagePointer.IN_PASSAGE:
        heading = doc.add_paragraph(style="qa")
        heading.add_run(heading_text, style="heading")
    passage_pointer.update_last_section(heading_text)

def add_end_break(doc, break_type=WD_BREAK.COLUMN):
    runs = doc.paragraphs[-1].runs
    if len(runs) == 0:
        doc.paragraphs[-1].add_run()
    doc.paragraphs[-1].runs[-1].add_break(break_type)

def format_url(version_id, book_code,chapter):
    return URL.format(version_id=version_id,book_code=book_code,chapter=chapter)

class FootnoteHandler:
    def __init__(self):
        self.text_notes = []
        self.next_note_label = "a"
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

class CopyrightHandler:
    def __init__(self, url):
        self.end_text = f"Read more at {url}"

    def get_copyright_statement(self, yvReader):
        copyright_block = yvReader.find("div", class_=re.compile("ChapterContent_version-copyright"))
        return copyright_block.getText() + "\n" + self.end_text

class PassagePointer:
    BEFORE_START = 0
    IN_PASSAGE = 1
    AFTER_END = 2

    def __init__(self, start_verse, end_verse):
        self.start_verse = start_verse
        self.end_verse = end_verse
        self.last_section = None
        self.state = PassagePointer.BEFORE_START
    
    def update_last_section(self, section):
        self.last_section = section
    
    def update_state(self, verse_text):
        current_verse = int(verse_text)
        if current_verse >= self.start_verse:
            self.state = PassagePointer.IN_PASSAGE
        if self.end_verse != -1 and current_verse > self.end_verse:
            self.state = PassagePointer.AFTER_END
    
def get_passage(version_id, book_code,chapter):
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

def add_passage(doc, version_id="113", book_code="PSA",chapter="119", start_verse=1, end_verse=-1):
    yvReader = get_passage(version_id, book_code, chapter)

    copyright_handler = CopyrightHandler(format_url(version_id, book_code, chapter))
    footnotes_handler = FootnoteHandler()
    passage_pointer = PassagePointer(start_verse, end_verse)

    chapter = yvReader.find("div", class_=re.compile("ChapterContent_chapter"))
    chapter_title = yvReader.find("div", class_=re.compile("ChapterContent_reader")).find("h1").getText()

    doc.paragraphs[0].add_run(chapter_title, style="chapter_heading")

    for chapter_section in chapter.find_all(recursive=False):
        section_type = re.findall("^ChapterContent_([a-zA-Z0-9]*)_*.*$", chapter_section["class"][0])[0]
        if section_type in ["p", "q1", "q2", "q3", "qa", "d", "pc", "m"]:
            doc_paragraph = {"paragraph": False, "doc": doc, "create": lambda doc: doc.add_paragraph(style=section_type)}
            if passage_pointer.state == PassagePointer.IN_PASSAGE:
                doc_paragraph["paragraph"] = doc_paragraph["create"](doc)
            
            for paragraph_section in chapter_section.find_all(recursive=False):
                paragraph_section_type = re.findall("^ChapterContent_([a-zA-Z0-9]*)_*.*$", paragraph_section["class"][0])[0]
                if paragraph_section_type == "verse":
                    for verse_section in paragraph_section.find_all(recursive=False):
                        add_verse_section(doc_paragraph, verse_section, footnotes_handler, passage_pointer)
                        if passage_pointer.state == PassagePointer.AFTER_END: break
                elif paragraph_section_type in ["content", "heading"]:
                    add_verse_section(doc_paragraph, paragraph_section, footnotes_handler, passage_pointer)
                else:
                    print(f"Unexpected part of section '{paragraph_section}' found.")
                if passage_pointer.state == PassagePointer.AFTER_END: break
            if passage_pointer.state == PassagePointer.AFTER_END: break
        elif section_type in ["s", "s1"]:
            add_heading_section(doc, chapter_section.getText(), passage_pointer)
            
        elif section_type == "b":
            if passage_pointer.IN_PASSAGE:
                doc.add_paragraph(style="blank_line")
        else:
            print(f"Unexpected section type '{section_type}' found.")

    doc.add_paragraph(footnotes_handler.print_notes(), style="footnotes")
    doc.add_paragraph(copyright_handler.get_copyright_statement(yvReader), style="copyright")

doc = Document()
# configure_columns(doc)
add_styles(doc)

for version in [101, 41, 139, 1819]:
    section = doc.sections[-1]
    section_1, section_2 = configure_portrait_parallel(doc)
    add_passage(section_1, version, "ACT", 17, 1, -1)
    add_passage(section_2, 113, "ACT", 17, 1, -1)
    doc.add_section()

doc.save("generated/out.docx")
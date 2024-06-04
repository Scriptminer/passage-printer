import re

from Version import Version
from FootnoteHandler import FootnoteHandler
from PassagePointer import PassagePointer
from PassageTools import get_passage, format_url

class Passage:
    def __init__(self, version_id="113", book_code="MRK", chapter="1", start_verse=1, end_verse=-1):
        self.version = Version(version_id)
        self.book_code, self.chapter, self.start_verse, self.end_verse = book_code, chapter, start_verse, end_verse
        print(f"Loading passage: {self}...")

        yvReader = get_passage(version_id, book_code, chapter)
        self.copyright_statement = self.get_copyright_statement(yvReader)
        self.readmore_statement = f"Read more at {format_url(self.version.version_id, self.book_code, self.chapter)}"
        self.footnotes_handler = FootnoteHandler()
        self.passage_pointer = PassagePointer(start_verse, end_verse)

        self.chapter_content = yvReader.find("div", class_=re.compile("ChapterContent_chapter"))
        self.chapter_title = yvReader.find("div", class_=re.compile("ChapterContent_reader")).find("h1").getText()

        print(f"Loading passage {self} complete.")
    
    def write_to(self, doc, config=None):
        doc.paragraphs[0].add_run(self.version.name, style="heading")
        doc.add_paragraph().add_run(self.chapter_title, style="chapter_heading")

        for chapter_section in self.chapter_content.find_all(recursive=False):
            section_type = re.findall("^ChapterContent_([a-zA-Z0-9]*)_*.*$", chapter_section["class"][0])[0]
            if section_type in ["p", "q1", "q2", "q3", "qa", "d", "pc", "m"]:
                doc_paragraph = {"paragraph": False, "doc": doc, "create": lambda doc: doc.add_paragraph(style=section_type)}
                if self.passage_pointer.state == PassagePointer.IN_PASSAGE:
                    doc_paragraph["paragraph"] = doc_paragraph["create"](doc)
                
                for paragraph_section in chapter_section.find_all(recursive=False):
                    paragraph_section_type = re.findall("^ChapterContent_([a-zA-Z0-9]*)_*.*$", paragraph_section["class"][0])[0]
                    if paragraph_section_type == "verse":
                        for verse_section in paragraph_section.find_all(recursive=False):
                            self.add_verse_section(doc_paragraph, verse_section, self.footnotes_handler, self.passage_pointer)
                            if self.passage_pointer.state == PassagePointer.AFTER_END: break
                    elif paragraph_section_type in ["content", "heading"]:
                        self.add_verse_section(doc_paragraph, paragraph_section, self.footnotes_handler, self.passage_pointer)
                    else:
                        print(f"Unexpected part of section '{paragraph_section}' found.")
                    if self.passage_pointer.state == PassagePointer.AFTER_END: break
                if self.passage_pointer.state == PassagePointer.AFTER_END: break
            elif section_type in ["s", "s1"]:
                self.add_heading_section(doc, chapter_section.getText(), self.passage_pointer)
                
            elif section_type == "b":
                if self.passage_pointer.IN_PASSAGE:
                    doc.add_paragraph(style="blank_line")

            elif section_type == "label":
                pass # Skip labels

            else:
                print(f"Unexpected section type '{section_type}' found. Section contents: {chapter_section}")

        doc.add_paragraph(self.footnotes_handler.print_notes(), style="footnotes")
        doc.add_paragraph(self.copyright_statement + "\n" + self.readmore_statement, style="copyright")

    def add_verse_section(self, paragraph, verse_section_data, footnotes_handler, passage_pointer):
        extracted_section_type = re.findall("^ChapterContent_([a-zA-Z0-9]*)_*.*$", verse_section_data["class"][0])
        verse_section_type = extracted_section_type[0] if len(extracted_section_type) > 0 else verse_section_data["class"][0]
        content = verse_section_data.getText()

        if verse_section_type == "label":
            passage_pointer.update_state(content)
        
        if passage_pointer.state != PassagePointer.IN_PASSAGE:
            return
        
        if paragraph["paragraph"] == False:
            self.add_heading_section(paragraph["doc"], passage_pointer.last_section, passage_pointer) # Add the previous heading
            paragraph["paragraph"] = paragraph["create"](paragraph["doc"])
        
        if verse_section_type == "note":
            content = f"[{footnotes_handler.add_note(verse_section_data)}]"
        
        try:
            paragraph["paragraph"].add_run(content, style=verse_section_type)
        except KeyError:
            print(f"Encountered unexpected verse section type '{verse_section_type}' at v{passage_pointer}. Treating the following as plain text: '{content}'.")

    def add_heading_section(self, paragraph, heading_text, passage_pointer):
        if heading_text and passage_pointer.state == PassagePointer.IN_PASSAGE:
            heading = paragraph.add_paragraph(style="qa")
            heading.add_run(heading_text, style="heading")
        passage_pointer.update_last_section(heading_text)

    def get_copyright_statement(self, yvReader):
        if self.version.custom_copyright_statement:
            copyright_statement = self.version.custom_copyright_statement
        else:
            # Use copyright statement from bible.com directly
            copyright_block = yvReader.find("div", class_=re.compile("ChapterContent_version-copyright"))
            first_section = copyright_block.find("div", recursive=False)
            copyright_statement = first_section.getText()
        return copyright_statement

    def __str__(self):
        end_verse = "end" if self.end_verse == -1 else self.end_verse 
        return f"{self.book_code} {self.chapter}:{self.start_verse}-{end_verse} ({self.version})"
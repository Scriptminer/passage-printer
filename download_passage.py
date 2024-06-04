from Passage import Passage
from DocumentTools import create_document, configure_parallel, configure_singular, add_styles
from PassageTools import resolve_version

def generate_regular_cafe_handout(book_code, chapter, start_verse=1, end_verse=-1):
    doc = create_document()
    add_styles(doc)

    for version in [101, 41, 139, 1819, 73]:
        section_1, section_2 = configure_parallel(doc, page_size="A4", portrait=True)
        Passage(version, book_code, chapter, start_verse, end_verse).write_to(section_1)
        Passage(113, book_code, chapter, start_verse, end_verse).write_to(section_2)
        doc.add_section()

    section = configure_singular(doc, page_size="A5", portrait=True)
    Passage(113, book_code, chapter, start_verse, end_verse).write_to(section)
    
    return doc

def generate_single_page(version, book_code, chapter, start_verse=1, end_verse=-1):
    doc = create_document()
    add_styles(doc)
    cell = configure_singular(doc, page_size="A4", portrait=True)
    Passage(version, book_code, chapter, start_verse, end_verse).write_to(cell)
    doc.add_section()

    return doc

def generate_verses_cutout_page(version_names, book_code, chapter, start_verse=1, end_verse=-1):
    doc = create_document()
    add_styles(doc)
    for version_name in version_names:
        cell = configure_singular(doc, page_size="A4", portrait=True)
        Passage(resolve_version(version_name), book_code, chapter, start_verse, end_verse).write_to(cell)
        cell.add_paragraph()
    
    return doc

doc = generate_regular_cafe_handout("EXO", 3, 1, 15)
# doc = generate_single_page(73, "EPH", 4)

# doc = generate_verses_cutout_page(["MALDIVIAN"]*2 + ["SIMPLIFIED CHINESE"]*8 + ["ENGLISH"]*10 + ["GERMAN"]*1 + ["JAPANESE"]*1 + ["TRADITIONAL CHINESE"]*1, "JHN", 3, 16, 17)
doc.save("generated/out.docx")
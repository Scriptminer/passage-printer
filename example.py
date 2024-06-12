from PrintoutFormats import generate_regular_multilingual_handout, generate_multiversion_handout, generate_single_page, generate_verses_cutout_page
from Passage import Passage

doc = generate_regular_multilingual_handout("EXO", 3, 1, 15)
Passage(113, "JHN", 3, 1, 16).write_to(doc)
# doc = generate_single_page(73, "EPH", 4)

# doc = generate_verses_cutout_page(["MALDIVIAN"]*2 + ["SIMPLIFIED CHINESE"]*8 + ["ENGLISH"]*10 + ["GERMAN"]*1 + ["JAPANESE"]*1 + ["TRADITIONAL CHINESE"]*1, "JHN", 3, 16, 17)
doc.save("generated/out.docx")
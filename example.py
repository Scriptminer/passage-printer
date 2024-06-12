from PrintoutFormats import generate_regular_multilingual_handout, generate_multiversion_handout, generate_single_page, generate_verses_cutout_page
from Passage import Passage

# Create a standard multilingual handout, such as for an "International Café" Bible study
doc1 = generate_regular_multilingual_handout("EXO", 3, 1, 15)
doc1.save("generated/example1.docx")

# Create a printout, then add separate passages onto it
doc2 = generate_single_page(113, "MAT", 1)
Passage(113, "MRK", 1).write_to(doc2)
Passage(113, "LUK", 1).write_to(doc2)
doc2.save("generated/example2.docx")

# Create a page with several short verses on one page
doc3 = generate_verses_cutout_page(["MALDIVIAN"]*2 + ["SIMPLIFIED CHINESE"]*8 + ["ENGLISH"]*10 + ["GERMAN"]*1 + ["JAPANESE"]*1 + ["TRADITIONAL CHINESE"]*1, "JHN", 3, 16, 17)
doc3.save("generated/example3.docx")

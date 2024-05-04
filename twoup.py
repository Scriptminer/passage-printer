from pypdf import PageObject, PaperSize, PdfReader, PdfWriter, Transformation

def render_two_up_horizontal(page):
    # page.scale_by(PaperSize.A5.height / PaperSize.A4.height)
    result_page = PageObject.create_blank_page(width=PaperSize.A4.width, height=PaperSize.A4.height)
    result_page.merge_transformed_page(page, Transformation().rotate(90).translate(PaperSize.A4.width,0))
    result_page.merge_transformed_page(page, Transformation().rotate(90).translate(PaperSize.A4.width,PaperSize.A4.height/2))
    return result_page

def add_pages(writer, page, count):
    for _ in range(count):
        writer.add_page(page)

pages = PdfReader("generated/Acts17.pdf").pages

writer = PdfWriter()
add_pages(writer, pages[0], 2)
add_pages(writer, pages[1], 3)
add_pages(writer, pages[2], 1)
add_pages(writer, pages[3], 1)
add_pages(writer, render_two_up_horizontal(pages[4]), 4)
writer.write("generated/Acts17cafe.pdf")
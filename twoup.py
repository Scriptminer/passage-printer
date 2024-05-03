from pypdf import PaperSize, PdfReader, PdfWriter, Transformation

def render_two_up_horizontal(writer, page):
    page.scale_by(PaperSize.A5.height / PaperSize.A4.height)
    result_page = writer.add_blank_page(width=PaperSize.A4.width, height=PaperSize.A4.height)
    result_page.merge_transformed_page(page, Transformation().rotate(90).translate(PaperSize.A4.width,0))
    result_page.merge_transformed_page(page, Transformation().rotate(90).translate(PaperSize.A4.width,PaperSize.A4.height/2))

page_to_duplicate = PdfReader("english.pdf").pages[0]
writer = PdfWriter()
render_two_up_horizontal(writer, page_to_duplicate)
writer.write("out.pdf")
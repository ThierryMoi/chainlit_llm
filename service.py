import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
from PyPDF2 import PdfReader


def ocr_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    print(pdf_document.page_count)
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)
        print(len(image_list))
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_data = base_image["image"]

            image = Image.open(io.BytesIO(image_data))
            text += pytesseract.image_to_string(image)

    return text


def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            return text


import fitz


def extract_text(pdf_path):

    document = fitz.open(pdf_path)

    full_text = ""

    for page in document:
        text = page.get_text()
        full_text += text


    document.close()

    return full_text
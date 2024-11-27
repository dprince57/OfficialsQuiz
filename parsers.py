import pdfplumber
import sys

def inspect_pdf(file_path):
    """
    Inspect raw text from the PDF to understand its structure.
    """
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"--- Page {i+1} ---")
            print(page.extract_text())

inspect_pdf("q1.pdf")
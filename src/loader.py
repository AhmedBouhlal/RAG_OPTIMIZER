import os
import pdfplumber
import pandas as pd
from docx import Document
from bs4 import BeautifulSoup
import markdown


def load_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_pdf(path):
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def load_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])


def load_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup.get_text()

def load_md(path):
    with open(path, "r", encoding="utf-8") as f:
        html = markdown.markdown(f.read())
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def load_csv(path):
    df = pd.read_csv(path)
    return df.to_string()

import re
import unicodedata
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """
    Clean and normalize text from books, PDFs, HTML, and general documents.

    Steps:
    1. Remove HTML tags
    2. Normalize unicode characters
    3. Remove excessive whitespace
    4. Fix broken line breaks from PDFs
    5. Normalize punctuation spacing
    """

    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # Normalize unicode (fix weird characters)
    text = unicodedata.normalize("NFKC", text)

    # Replace line breaks and tabs with spaces
    text = re.sub(r"[\n\r\t]+", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Fix spaces before punctuation
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def load_documents(input_dict):

    data_dir = input_dict["data_dir"]
    documents = []

    files = sorted(os.listdir(data_dir))

    for i, file in enumerate(files):

        path = os.path.join(data_dir, file)
        ext = file.split(".")[-1].lower()

        try:

            if ext == "txt":
                text = load_txt(path)

            elif ext == "pdf":
                text = load_pdf(path)

            elif ext == "docx":
                text = load_docx(path)

            elif ext == "html":
                text = load_html(path)

            elif ext == "csv":
                text = load_csv(path)
            
            elif ext == "md":
                text = load_md(path)

            else:
                continue

            if not text or len(text.strip()) == 0:
                continue

            doc = {
                "doc_id": f"doc_{i+1:03d}",
                "file_name": file,
                "source": ext,
                "path": path,
                "size_kb": os.path.getsize(path) / 1024,
                "text": clean_text(text)
            }

            documents.append(doc)

        except Exception as e:
            print(f"Error loading {file}: {e}")

    return {"documents": documents}

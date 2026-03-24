# src/loader.py
import os
import json
import pdfplumber
from docx import Document
import pandas as pd
from bs4 import BeautifulSoup

# -----------------------------
# Document Loaders
# -----------------------------
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

def load_csv(path):
    df = pd.read_csv(path)
    return df.to_string()

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def json_to_text(data):
    """Convert JSON data to readable text format for RAG processing"""
    if isinstance(data, list):
        texts = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                text = f"Item {i+1}:\n"
                for key, value in item.items():
                    if isinstance(value, list):
                        text += f"  {key}: {', '.join(map(str, value))}\n"
                    elif isinstance(value, dict):
                        text += f"  {key}:\n"
                        for subkey, subvalue in value.items():
                            text += f"    {subkey}: {subvalue}\n"
                    else:
                        text += f"  {key}: {value}\n"
                texts.append(text)
            else:
                texts.append(f"Item {i+1}: {str(item)}")
        return "\n".join(texts)
    elif isinstance(data, dict):
        text = ""
        for key, value in data.items():
            if isinstance(value, list):
                text += f"{key}: {', '.join(map(str, value))}\n"
            elif isinstance(value, dict):
                text += f"{key}:\n"
                for subkey, subvalue in value.items():
                    text += f"  {subkey}: {subvalue}\n"
            else:
                text += f"{key}: {value}\n"
        return text
    else:
        return str(data)

# -----------------------------
# Load all documents from folder
# -----------------------------
def load_documents(input_dict):
    data_dir = input_dict["data_dir"]
    documents = []

    files = sorted(os.listdir(data_dir))

    for i, file in enumerate(files):
        path = os.path.join(data_dir, file)
        ext = file.split(".")[-1].lower()

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
        elif ext == "json":
            json_data = load_json(path)
            text = json_to_text(json_data)
        else:
            continue

        doc = {
            "doc_id": f"doc_{i+1:03d}",
            "file_name": file,
            "source": ext,
            "text": text
        }
        documents.append(doc)

    return {"documents": documents}

# -----------------------------
# Load all evaluation JSONs from folder
# -----------------------------
def load_evaluation(input_dict):
    eval_dir = input_dict["eval_dir"]
    evaluations = []

    files = sorted(os.listdir(eval_dir))
    for file in files:
        if not file.endswith(".json"):
            continue
        path = os.path.join(eval_dir, file)
        data = load_json(path)

        # Normalize answer field to always be a list of strings
        for item in data:
            if "answer" in item and isinstance(item["answer"], str):
                item["answer"] = [item["answer"]]
            elif "answer" not in item:
                item["answer"] = []

        evaluations.append({
            "file_name": file,
            "data": data
        })

    return {"evaluations": evaluations}
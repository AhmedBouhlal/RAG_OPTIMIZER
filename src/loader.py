import os

def load_documents(input_dict):
    data_dir = input_dict["data_dir"]
    documents = []

    files = sorted(os.listdir(data_dir))  # sorted for consistent order

    for i, file in enumerate(files):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(data_dir, file)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.strip():  # skip empty files
            continue

        doc = {
            "doc_id": f"doc_{i+1:03d}",
            "file_name": file,
            "text": text,
            "num_words": len(text.split())
        }

        documents.append(doc)

    return {"documents": documents}
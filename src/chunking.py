def chunk_documents(input_dict):

    documents = input_dict["documents"]
    config = input_dict["config"]

    chunk_size = config["chunk_size"]
    overlap = config["overlap"]

    step = chunk_size - overlap

    chunks = []

    for doc in documents:

        doc_id = doc["doc_id"]
        text = doc["text"]

        words = text.split()

        start = 0
        chunk_index = 0

        while start < len(words):

            end = start + chunk_size

            chunk_words = words[start:end]

            if not chunk_words:
                break

            chunk_text = " ".join(chunk_words)

            chunk = {
                "chunk_id": f"{doc_id}_chunk_{chunk_index:04d}",
                "doc_id": doc_id,
                "text": chunk_text,
                "start_word": start,
                "end_word": min(end, len(words))
            }

            chunks.append(chunk)

            chunk_index += 1
            start += step

    output = {
        "chunks": chunks
    }

    return output

from src.retrieval import retrieve_chunks
from src.keyword_index import bm25_search
from src.rrf import reciprocal_rank_fusion


def hybrid_retrieve(input_dict):

    query = input_dict["query"]
    config = input_dict["config"]
    index = input_dict["index"]
    chunks = input_dict["chunks"]
    bm25 = input_dict["bm25"]

    top_k = config["top_k"]

    # semantic search
    semantic = retrieve_chunks({
        "query": query,
        "config": config,
        "index": index,
        "chunks": chunks
    })["results"]

    # keyword search
    keyword = bm25_search({
        "query": query,
        "bm25": bm25,
        "chunks": chunks,
        "top_k": top_k
    })["results"]

    # RRF fusion
    fused = reciprocal_rank_fusion(semantic, keyword)

    return {
        "results": fused[:top_k]
    }
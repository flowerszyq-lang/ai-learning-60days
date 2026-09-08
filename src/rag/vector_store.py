# src/rag/vector_store.py (ChromaDB 版)
import chromadb
from chromadb.utils import embedding_functions

# 初始化 ChromaDB 客户端（内存模式）
_client = chromadb.Client()
_collection = _client.get_or_create_collection(
    name="banking_docs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)

def store_documents(chunks):
    """存储文档到向量库"""
    ids = [chunk["id"] for chunk in chunks]
    contents = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    _collection.add(
        ids=ids,
        documents=contents,
        metadatas=metadatas
    )
    return len(ids)

def search_documents(query: str, top_k=3):
    """检索相关文档"""
    results = _collection.query(
        query_texts=[query],
        n_results=top_k
    )
    docs = []
    for i in range(len(results['ids'][0])):
        docs.append({
            "id": results['ids'][0][i],
            "content": results['documents'][0][i],
            "metadata": results['metadatas'][0][i]
        })
    return docs
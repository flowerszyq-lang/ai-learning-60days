# src/rag/embedder.py

from sentence_transformers import SentenceTransformer

# 加载轻量级模型，输出维度 384
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_text(text: str):
    model = get_model()
    return model.encode(text).tolist()

def embed_documents(texts):
    model = get_model()
    return model.encode(texts).tolist()
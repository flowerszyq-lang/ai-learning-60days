# src/routers/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.rag import loader, vector_store

router = APIRouter(prefix="/api/rag", tags=["RAG"])

class AskRequest(BaseModel):
    question: str

@router.post("/ingest")
async def ingest_documents():
    try:
        docs = loader.load_banking_documents()
        chunks = loader.chunk_texts(docs)
        count = vector_store.store_documents(chunks)
        return {"status": "success", "ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_documents(query: str, top_k: int = 3):
    try:
        docs = vector_store.search_documents(query, top_k)
        return {"query": query, "results": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_question(request: AskRequest):
    try:
        docs = vector_store.search_documents(request.question, top_k=3)
        if not docs:
            return {"answer": "抱歉，未找到相关信息。", "sources": []}
        context = "\n\n".join([doc["content"] for doc in docs])
        answer = f"基于检索到的银行政策：\n\n{context}\n\n针对您的问题“{request.question}”，建议您参考以上政策信息。如有疑问，请咨询银行客服。"
        return {"answer": answer, "sources": [{"content": doc["content"]} for doc in docs]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ping")
async def ping():
    return {"message": "RAG router alive"}
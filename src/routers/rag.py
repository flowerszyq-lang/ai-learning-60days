# src/routers/rag.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.rag import loader, vector_store
import httpx

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
    # 1. 检索相关文档（已有代码）
    docs = vector_store.search_documents(request.question, top_k=3)
    context = "\n\n".join([doc["content"] for doc in docs])

    # 2. 构造 Prompt
    prompt = f"""你是一位银行客服专家。请基于以下资料回答用户问题。
如果资料中没有相关信息，请明确告知用户未找到。

参考资料：
{context}

用户问题：{request.question}

回答："""

    # 3. 调用 Ollama
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,   # 降低随机性，使回答更精准
                    "top_p": 0.9
                }
            }
        )
        result = response.json()
        answer = result.get("response", "模型未返回有效回答")

    return {
        "answer": answer,
        "sources": [{"content": doc["content"]} for doc in docs]
    }

@router.get("/ping")
async def ping():
    return {"message": "RAG router alive"}
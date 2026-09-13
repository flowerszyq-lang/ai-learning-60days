# src/routers/rag.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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

from src.services.memory import memory_store

class AskRequest(BaseModel):
    question: str
    session_id: str = "default"   # 新增：会话 ID

@router.post("/ask")
async def ask_question(request: AskRequest):
    # 1. 检索相关文档
    docs = vector_store.search_documents(request.question, top_k=3)
    context = "\n\n".join([doc["content"] for doc in docs])

    # 2. 系统提示词（含检索上下文）
    system_prompt = (
        "你是一位银行客服专家。请基于以下资料回答用户问题。\n"
        "如果资料中没有相关信息，请明确告知用户未找到。\n\n"
        f"参考资料：\n{context}"
    )

    # 3. 取出该会话的历史
    history = memory_store.get_history(request.session_id)

    # 4. 组装 messages（system + history + 当前问题）
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": request.question})

    # 5. 调用 Ollama 的 /api/chat（原生支持多轮）
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen2.5:7b",
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.3}
            }
        )
        result = response.json()
        answer = result.get("message", {}).get("content", "")

    # 6. 把本轮问答写入记忆
    memory_store.add_message(request.session_id, "user", request.question)
    memory_store.add_message(request.session_id, "assistant", answer)

    return {
        "session_id": request.session_id,
        "answer": answer,
        "sources": [{"content": doc["content"]} for doc in docs]
    }

# 可选：清空会话
@router.post("/ask/clear")
async def clear_session(session_id: str):
    memory_store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}

@router.post("/ask-stream")
async def ask_stream(request: AskRequest, session_id: str = "default"):
    # 检索文档 ...
    # 构造 Prompt（包含历史）...
    # 调用 Ollama 流式接口
    async def generate():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                    "POST",
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "qwen2.5:7b",
                        "prompt": prompt,
                        "stream": True
                    }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        yield data.get("response", "")
    return StreamingResponse(generate(), media_type="text/plain")

@router.get("/ping")
async def ping():
    return {"message": "RAG router alive"}
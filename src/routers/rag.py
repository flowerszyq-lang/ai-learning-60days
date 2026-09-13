# src/routers/rag.py
import json
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.rag import loader, vector_store
from src.services.memory import memory_store

router = APIRouter(prefix="/api/rag", tags=["RAG"])

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "qwen2.5:7b"


class AskRequest(BaseModel):
    question: str
    session_id: str = "default"


# ---------------------------------------------------------
# 1. 导入文档
# ---------------------------------------------------------
@router.post("/ingest")
async def ingest_documents():
    try:
        docs = loader.load_banking_documents()
        chunks = loader.chunk_texts(docs)
        count = vector_store.store_documents(chunks)
        return {"status": "success", "ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# 2. 纯检索（不经过 LLM）
# ---------------------------------------------------------
@router.get("/search")
async def search_documents(query: str, top_k: int = 3):
    try:
        docs = vector_store.search_documents(query, top_k)
        return {"query": query, "results": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# 3. 问答（非流式）
# ---------------------------------------------------------
@router.post("/ask")
async def ask_question(request: AskRequest):
    try:
        # 1. 检索相关文档
        docs = vector_store.search_documents(request.question, top_k=3)
        context = "\n\n".join([doc["content"] for doc in docs])

        # 2. 系统提示词（只负责角色，不携带 context）
        system_prompt = (
            "你是一位专业的银行客服专家，回答要准确、简洁、礼貌。"
            "如果参考资料中没有相关信息，请明确告知用户未找到，不要编造内容。"
        )

        # 3. 取出该会话的历史
        history = memory_store.get_history(request.session_id)

        # 4. 组装 messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        # 5. 把 context + question 一起放在 user message 里
        user_message = f"""请根据以下参考资料回答问题。

参考资料：
{context}

用户问题：{request.question}

请基于上述参考资料给出准确回答。"""
        messages.append({"role": "user", "content": user_message})

        # 6. 调用 Ollama（trust_env=False 避免代理干扰）
        async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL_NAME,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
            )

            print(f"[DEBUG] Ollama status: {response.status_code}")
            print(f"[DEBUG] Messages count: {len(messages)}")

            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama error {response.status_code}: {response.text[:300]}"
                )

            result = response.json()
            answer = result.get("message", {}).get("content", "")

        # 7. 写入记忆
        memory_store.add_message(request.session_id, "user", request.question)
        memory_store.add_message(request.session_id, "assistant", answer)

        return {
            "session_id": request.session_id,
            "answer": answer,
            "sources": [{"content": doc["content"]} for doc in docs]
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# 4. 问答（流式输出）
# ---------------------------------------------------------
@router.post("/ask-stream")
async def ask_stream(request: AskRequest):
    # 1. 检索
    docs = vector_store.search_documents(request.question, top_k=3)
    context = "\n\n".join([doc["content"] for doc in docs])

    system_prompt = (
        "你是一位专业的银行客服专家，回答要准确、简洁、礼貌。"
        "如果参考资料中没有相关信息，请明确告知用户未找到，不要编造内容。"
    )

    history = memory_store.get_history(request.session_id)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)

    user_message = f"""请根据以下参考资料回答问题。

参考资料：
{context}

用户问题：{request.question}

请基于上述参考资料给出准确回答。"""
    messages.append({"role": "user", "content": user_message})

    async def generate():
        full_answer = ""
        async with httpx.AsyncClient(timeout=120.0, trust_env=False) as client:
            async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": MODEL_NAME,
                        "messages": messages,
                        "stream": True,
                        "options": {"temperature": 0.3}
                    }
            ) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        full_answer += chunk
                        yield chunk

        # 流式结束后写入记忆
        memory_store.add_message(request.session_id, "user", request.question)
        memory_store.add_message(request.session_id, "assistant", full_answer)

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


# ---------------------------------------------------------
# 5. 清空会话记忆
# ---------------------------------------------------------
@router.post("/ask/clear")
async def clear_session(session_id: str):
    memory_store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}


# ---------------------------------------------------------
# 6. 健康检查
# ---------------------------------------------------------
@router.get("/ping")
async def ping():
    return {"message": "RAG router alive"}
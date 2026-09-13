# src/routers/agent.py
import json
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.agent.tools import get_tools_description
from src.agent.executor import execute_tool

router = APIRouter(prefix="/api/agent", tags=["Agent"])

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "qwen2.5:7b"

class AgentRequest(BaseModel):
    question: str

@router.post("/ask")
async def agent_ask(request: AgentRequest):
    tools_desc = get_tools_description()
    tool_prompt = json.dumps(tools_desc, ensure_ascii=False, indent=2)

    system_prompt = f"""你是一个银行智能助手。你可以使用以下工具来帮助用户：

{tool_prompt}

请根据用户的问题，决定是否需要调用工具。如果需要，请输出 JSON 格式：
{{"tool": "工具名", "parameters": {{"参数名": "参数值"}}}}

如果不需要调用工具，直接回答用户问题。
只输出 JSON，不要有其他内容。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.question}
    ]

    async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
        # 第一次调用：让 LLM 决定调用哪个工具
        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.1}
            }
        )
        result = response.json()
        llm_output = result.get("message", {}).get("content", "").strip()
        print(f"[DEBUG] LLM output: {llm_output}")

        # 尝试解析 JSON
        try:
            tool_call = json.loads(llm_output)
        except json.JSONDecodeError:
            # 如果不是 JSON，直接作为回答返回
            return {"answer": llm_output, "tool_calls": []}

        tool_name = tool_call.get("tool")
        parameters = tool_call.get("parameters", {})

        # 执行工具
        tool_result = await execute_tool(tool_name, parameters)
        print(f"[DEBUG] Tool result: {tool_result}")

        # 第二次调用：把工具结果给 LLM，生成最终回答
        messages.append({"role": "assistant", "content": llm_output})
        messages.append({"role": "user", "content": f"工具执行结果：{json.dumps(tool_result, ensure_ascii=False)}\n请根据结果回答用户。"})

        final_response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.3}
            }
        )
        final_result = final_response.json()
        final_answer = final_result.get("message", {}).get("content", "")

    return {
        "answer": final_answer,
        "tool_calls": [{"tool": tool_name, "parameters": parameters, "result": tool_result}]
    }
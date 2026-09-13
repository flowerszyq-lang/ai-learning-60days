# src/agent/executor.py
import json
from src.agent.tools import TOOL_REGISTRY

async def execute_tool(tool_name: str, parameters: dict):
    """根据工具名和参数执行对应函数"""
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"未知工具: {tool_name}"}
    func = TOOL_REGISTRY[tool_name]["function"]
    try:
        result = await func(**parameters)
        return result
    except Exception as e:
        return {"error": str(e)}
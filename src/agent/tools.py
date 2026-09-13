# src/agent/tools.py
from typing import Dict, Any, Callable, Awaitable
from src.database import AsyncSessionLocal
from src.models.db_models import Customer, Transaction
from sqlalchemy import select
import uuid

# 工具注册表
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}

def register_tool(name: str, description: str, parameters: dict):
    def decorator(func: Callable[..., Awaitable[Any]]):
        TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": func
        }
        return func
    return decorator

# ---------- 工具 1：根据姓名查询客户 ----------
@register_tool(
    name="get_customer_by_name",
    description="根据客户姓名查询客户信息，返回客户ID、身份证号、手机号、风险等级",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "客户姓名"}
        },
        "required": ["name"]
    }
)
async def get_customer_by_name(name: str):
    async with AsyncSessionLocal() as db:
        stmt = select(Customer).where(Customer.name == name)
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        if not customer:
            return {"error": f"未找到姓名为 {name} 的客户"}
        return {
            "id": str(customer.id),
            "name": customer.name,
            "id_card": customer.id_card,
            "phone": customer.phone,
            "risk_level": customer.risk_level
        }

# ---------- 工具 2：查询客户交易 ----------
@register_tool(
    name="get_transactions_by_customer",
    description="根据客户ID查询该客户的所有交易记录",
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "客户ID（UUID格式）"}
        },
        "required": ["customer_id"]
    }
)
async def get_transactions_by_customer(customer_id: str):
    async with AsyncSessionLocal() as db:
        # 先查客户是否存在
        stmt = select(Customer).where(Customer.id == uuid.UUID(customer_id))
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        if not customer:
            return {"error": "客户不存在"}
        # 再查交易（这里简化：交易表没有直接关联客户，我们通过 account_id 关联，暂略）
        # 实际项目中应通过 account 表关联，这里仅演示
        return {"message": "交易查询功能待实现"}

# ---------- 工具 3：查询银行政策（RAG） ----------
@register_tool(
    name="search_bank_policy",
    description="根据关键词检索银行政策文档，返回相关条款",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "检索关键词"}
        },
        "required": ["query"]
    }
)
async def search_bank_policy(query: str):
    from src.rag import vector_store
    docs = vector_store.search_documents(query, top_k=3)
    return {"results": [doc["content"] for doc in docs]}

# 获取工具列表（用于构造 Prompt）
def get_tools_description():
    tools = []
    for name, info in TOOL_REGISTRY.items():
        tools.append({
            "name": name,
            "description": info["description"],
            "parameters": info["parameters"]
        })
    return tools
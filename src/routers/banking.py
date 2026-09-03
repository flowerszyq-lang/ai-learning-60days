from fastapi import APIRouter, HTTPException
from src.models.customer import Customer
from src.models.account import Account
from src.models.transaction import Transaction
import logging

logger = logging.getLogger(__name__)

# 相当于 Spring 的 @RequestMapping("/api/banking")
router = APIRouter(prefix="/api/banking", tags=["Banking"])

# 模拟内存数据库（后续会换成真实 DB）
fake_db = {
    "customers": [],
    "accounts": [],
    "transactions": []
}

@router.post("/customers", response_model=Customer)
async def create_customer(customer: Customer):
    """创建客户（自动校验入参）"""
    # 业务逻辑：存储客户（此处仅模拟）
    fake_db["customers"].append(customer.dict())
    logger.info(f"New customer created: {customer.name}")
    # 返回创建后的客户信息（Pydantic 自动转 JSON）
    return customer

@router.post("/accounts/{customer_id}/transactions", response_model=Transaction)
async def create_transaction(customer_id: str, transaction: Transaction):
    """为指定客户创建交易（注意：url 里的 customer_id 和 body 里的 account_id 逻辑独立，此处仅演示）"""
    # 模拟校验账户是否存在（略）
    logger.info(f"Transaction for customer {customer_id}: {transaction.amount}")
    fake_db["transactions"].append(transaction.dict())
    return transaction

# 一个小彩蛋接口：手动触发风险评分（展示你的数学优势）
@router.get("/customers/{customer_id}/risk-score")
async def calculate_risk_score(customer_id: str):
    """数学小彩蛋：基于正态分布思想计算简单的风险分"""
    import math
    import random

    # 模拟从数据库取数（随机生成 5~20 笔交易金额）
    sample_amounts = [random.randint(100, 10000) for _ in range(random.randint(5, 20))]

    if not sample_amounts:
        return {"customer_id": customer_id, "score": 0, "message": "无交易记录"}

    # 计算均值、标准差（数学专业优势在此）
    mean = sum(sample_amounts) / len(sample_amounts)
    variance = sum((x - mean) ** 2 for x in sample_amounts) / len(sample_amounts)
    std_dev = math.sqrt(variance)

    # 变异系数（CV）越大，说明交易波动大，风险越高
    cv = std_dev / mean if mean != 0 else 0

    # 映射到 0~100 的分值（简单逻辑）
    score = min(100, int(cv * 50))

    return {
        "customer_id": customer_id,
        "risk_score": score,
        "transaction_count": len(sample_amounts),
        "mean_amount": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "interpretation": "分值越高，交易波动风险越大"
    }
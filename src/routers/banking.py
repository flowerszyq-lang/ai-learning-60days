from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging
import math
import random

from src.models.customer import Customer as CustomerDTO
from src.models.transaction import Transaction as TransactionDTO
from src.models.db_models import Customer as CustomerDB, Transaction as TransactionDB
from src.database import AsyncSessionLocal
from pydantic import BaseModel

class CustomerResponse(BaseModel):
    id: str
    name: str
    id_card: str
    phone: str
    risk_level: str

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/banking", tags=["Banking"])

# 依赖注入：获取数据库会话
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# ----- 创建客户（写入数据库）-----
@router.post("/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerDTO, db: AsyncSession = Depends(get_db)):
    # 1. 检查身份证是否已存在
    stmt = select(CustomerDB).where(CustomerDB.id_card == customer.id_card)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="身份证号已注册")

    # 2. 创建数据库实体
    db_customer = CustomerDB(
        id=uuid.uuid4(),
        name=customer.name,
        id_card=customer.id_card,
        phone=customer.phone,
        risk_level=customer.risk_level
    )
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)

    logger.info(f"Customer created: {db_customer.name} (ID: {db_customer.id})")
    # 返回包含 id 的响应
    return CustomerResponse(
        id=str(db_customer.id),
        name=db_customer.name,
        id_card=db_customer.id_card,
        phone=db_customer.phone,
        risk_level=db_customer.risk_level
    )  # 注意最后的闭合括号

# ----- 创建交易（写入数据库）-----
@router.post("/accounts/{customer_id}/transactions", response_model=TransactionDTO)
async def create_transaction(customer_id: str, transaction: TransactionDTO, db: AsyncSession = Depends(get_db)):
    # 1. 验证客户是否存在（简单校验，实际项目中会更复杂）
    stmt = select(CustomerDB).where(CustomerDB.id == uuid.UUID(customer_id))
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    # 2. 创建交易实体
    db_txn = TransactionDB(
        id=uuid.uuid4(),
        account_id=uuid.UUID(transaction.account_id),
        amount=transaction.amount,
        type=transaction.type.value,  # 枚举转字符串
        note=transaction.note
    )
    db.add(db_txn)
    await db.commit()
    await db.refresh(db_txn)

    logger.info(f"Transaction created: {db_txn.id} for account {db_txn.account_id}")
    return TransactionDTO(
        transaction_id=str(db_txn.id),
        account_id=str(db_txn.account_id),
        amount=db_txn.amount,
        type=transaction.type,
        note=db_txn.note,
        created_at=db_txn.created_at
    )

# ----- 风险评分（保留数学计算，改为从数据库读取真实交易数据）-----
@router.get("/customers/{customer_id}/risk-score")
async def calculate_risk_score(customer_id: str, db: AsyncSession = Depends(get_db)):
    # 1. 验证客户存在
    stmt = select(CustomerDB).where(CustomerDB.id == uuid.UUID(customer_id))
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    # 2. 模拟从数据库获取该客户所有交易（此处为演示，仍使用随机数据）
    #    实际项目可以从 TransactionDB 表中查询 account_id 关联的交易
    sample_amounts = [random.randint(100, 10000) for _ in range(random.randint(5, 20))]

    if not sample_amounts:
        return {"customer_id": customer_id, "score": 0, "message": "无交易记录"}

    mean = sum(sample_amounts) / len(sample_amounts)
    variance = sum((x - mean) ** 2 for x in sample_amounts) / len(sample_amounts)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean if mean != 0 else 0
    score = min(100, int(cv * 50))

    return {
        "customer_id": customer_id,
        "risk_score": score,
        "transaction_count": len(sample_amounts),
        "mean_amount": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "interpretation": "分值越高，交易波动风险越大"
    }
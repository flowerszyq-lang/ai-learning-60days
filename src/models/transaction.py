from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class Transaction(BaseModel):
    """交易 DTO"""
    transaction_id: str = Field(..., min_length=1, description="交易ID")
    account_id: str = Field(..., description="账户ID")
    amount: float = Field(..., gt=0, description="交易金额，必须大于0")
    type: TransactionType = Field(..., description="交易类型: INCOME/EXPENSE")
    note: Optional[str] = Field(default=None, max_length=200, description="备注")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="交易时间")
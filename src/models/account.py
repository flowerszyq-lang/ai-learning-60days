from pydantic import BaseModel, Field
from typing import Optional

class Account(BaseModel):
    """账户 DTO"""
    account_id: str = Field(..., min_length=1, description="账号")
    customer_id: str = Field(..., description="所属客户ID")
    account_type: str = Field(..., description="账户类型: SAVINGS, CREDIT")
    balance: float = Field(..., ge=0, description="余额，不能为负数")
    status: str = Field(default="ACTIVE", description="状态: ACTIVE, FROZEN, CLOSED")
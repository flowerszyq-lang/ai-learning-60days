from pydantic import BaseModel, Field, field_validator
import re

class Customer(BaseModel):
    """客户信息 DTO 相当于 Java 的 @NotNull @Size"""
    name: str = Field(..., min_length=1, description="客户姓名，不能为空")
    id_card: str = Field(..., min_length=18, max_length=18, description="身份证号，18位")
    phone: str = Field(..., description="手机号，11位")
    risk_level: str = Field(default="LOW", description="风险等级: LOW, MEDIUM, HIGH")

    # 自定义校验器：类似 Java 的 @Pattern 或自定义校验注解
    @field_validator("id_card")
    @classmethod
    def validate_id_card(cls, v: str) -> str:
        # 简单校验：必须全是数字或X结尾（为了演示，不做复杂加权校验）
        if not re.match(r"^\d{17}[\dXx]$", v):
            raise ValueError("身份证号必须是18位，前17位数字，最后一位数字或X")
        return v.upper()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确，必须是11位且以1开头")
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        allowed = {"LOW", "MEDIUM", "HIGH"}
        if v.upper() not in allowed:
            raise ValueError("风险等级必须是 LOW, MEDIUM, HIGH 之一")
        return v.upper()
import httpx
import asyncio
import os
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://{HOST}:{PORT}"

async def test():
    """测试所有接口"""
    async with httpx.AsyncClient() as client:
        # 1. 测试健康检查
        resp = await client.get(f"{BASE_URL}/health")
        print("Health:", resp.json())

        # 2. 测试 Echo
        resp = await client.post(
            f"{BASE_URL}/echo",
            json={"message": "Hello AI", "user_id": "java_dev_001"}
        )
        print("Echo:", resp.json())

        # 3. 测试创建客户（Day 3 新增）
        resp = await client.post(
            f"{BASE_URL}/api/banking/customers",
            json={
                "name": "张伟",
                "id_card": "11010119900307666X",
                "phone": "13800138000",
                "risk_level": "MEDIUM"
            }
        )
        print("Customer:", resp.json())

        # 4. 测试创建交易（Day 3 新增）
        resp = await client.post(
            f"{BASE_URL}/api/banking/accounts/cust_001/transactions",
            json={
                "transaction_id": "TXN20260903001",
                "account_id": "ACC001",
                "amount": 500.00,
                "type": "EXPENSE",
                "note": "餐饮消费"
            }
        )
        print("Transaction:", resp.json())

        # 5. 风险评分（数学彩蛋，Day 3 新增）
        resp = await client.get(f"{BASE_URL}/api/banking/customers/cust_001/risk-score")
        print("Risk Score:", resp.json())

if __name__ == "__main__":
    asyncio.run(test())
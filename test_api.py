import httpx
import asyncio
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://{HOST}:{PORT}"

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. 健康检查
        resp = await client.get(f"{BASE_URL}/health")
        print("Health:", resp.json())

        # 2. Echo
        resp = await client.post(
            f"{BASE_URL}/echo",
            json={"message": "Hello AI", "user_id": "java_dev_001"}
        )
        print("Echo:", resp.json())

        # 3. 创建客户（使用新身份证号，避免重复）
        customer_data = {
            "name": "王五",
            "id_card": "11010119900888888X",  # 新身份证号
            "phone": "13700137000",
            "risk_level": "LOW"
        }
        resp = await client.post(
            f"{BASE_URL}/api/banking/customers",
            json=customer_data
        )
        if resp.status_code != 200:
            print(f"Create customer failed: {resp.status_code} - {resp.text}")
            return
        customer = resp.json()
        print("Customer:", customer)

        # 从响应中获取客户 ID（响应中包含 'id' 字段）
        customer_id = customer.get("id")
        if not customer_id:
            print("No customer ID in response")
            return

        # 4. 创建交易（使用正确的 customer_id）
        transaction_data = {
            "transaction_id": f"TXN{uuid.uuid4().hex[:8].upper()}",
            "account_id": str(uuid.uuid4()),  # 暂时生成一个合法 UUID
            "amount": 500.00,
            "type": "EXPENSE",
            "note": "餐饮消费"
        }
        resp = await client.post(
            f"{BASE_URL}/api/banking/accounts/{customer_id}/transactions",
            json=transaction_data
        )
        if resp.status_code != 200:
            print(f"Create transaction failed: {resp.status_code} - {resp.text}")
            return
        print("Transaction:", resp.json())

if __name__ == "__main__":
    asyncio.run(test())
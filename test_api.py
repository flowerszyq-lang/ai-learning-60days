import httpx
import asyncio
import os
from dotenv import load_dotenv

# 加载 .env（虽然 httpx 不需要，但为了演示读取配置）
load_dotenv()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://{HOST}:{PORT}"

async def test():
    async with httpx.AsyncClient() as client:
        # 测试 health
        resp = await client.get(f"{BASE_URL}/health")
        print("Health:", resp.json())

        # 测试 echo
        resp = await client.post(
            f"{BASE_URL}/echo",
            json={"message": "Hello AI", "user_id": "java_dev_001"}
        )
        print("Echo:", resp.json())

if __name__ == "__main__":
    asyncio.run(test())
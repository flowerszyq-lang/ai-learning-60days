import httpx
import asyncio

async def test():
    # 测试 health
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://127.0.0.1:8000/health")
        print("Health:", resp.json())

        # 测试 echo
        resp = await client.post(
            "http://127.0.0.1:8000/echo",
            json={"message": "Hello AI", "user_id": "java_dev_001"}
        )
        print("Echo:", resp.json())

if __name__ == "__main__":
    asyncio.run(test())
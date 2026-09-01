from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Learning Service", version="0.1.0")

# ----- 日志中间件（相当于 Spring Filter） -----
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# ----- 健康检查 -----
@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok"}

# ----- Echo 接口（模拟 AI 回复）-----
class EchoRequest(BaseModel):
    message: str
    user_id: str | None = None

@app.post("/echo")
async def echo(request: EchoRequest, lang: str = "en"):
    logger.info(f"Echo from user {request.user_id}: {request.message}")

    if lang == "zh":
        reply = f"你说了: {request.message}"
    else:
        reply = f"You said: {request.message}"

    return {
        "received": request.message,
        "user_id": request.user_id,
        "reply": reply
    }

# ----- 路径参数测试 -----
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    logger.info(f"Fetching item {item_id}")
    return {"item_id": item_id, "name": f"Item {item_id}"}
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
import sys

# 导入我们的配置
from .config import settings
# ----- 配置日志（动态级别）-----
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# ----- 创建应用（使用配置中的名称）-----
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    debug=settings.debug
)

# ----- 日志中间件 -----
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
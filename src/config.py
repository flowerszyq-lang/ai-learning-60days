from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用名称
    app_name: str = "AI Learning Service"
    # 调试模式
    debug: bool = False
    # 日志级别
    log_level: str = "INFO"
    # 服务地址
    host: str = "127.0.0.1"
    # 服务端口
    port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/banking"
    class Config:
        # 指定从 .env 文件读取
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建一个全局配置实例（相当于 Spring 的 @Component）
settings = Settings()
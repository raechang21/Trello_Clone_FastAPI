from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # 1. 定義變數與型別（強型別約束）
    # 若 .env 中不存在且未設預設值，啟動時會拋出 ValidationError
    PORT: int = 3000
    MONGO_URL: str = ""

    # 2. 配置 Pydantic 讀取 .env 的行為
    model_config = SettingsConfigDict(
        env_file=".env",           # 指定讀取的檔案
        env_file_encoding="utf-8", 
        extra="ignore"             # 忽略 .env 中未定義在 Class 裡的額外變數
    )

# 實例化供全域調用
settings = Settings()
"""
環境設定模組
從 .env 檔案載入環境變數
對應 tasks.md T022
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    應用程式設定
    自動從環境變數或 .env 檔案載入
    """

    # 資料庫設定
    DATABASE_URL: str = Field(
        default="sqlite:///./vibe_note.db",
        description="資料庫連線 URL"
    )
    SQL_ECHO: bool = Field(
        default=False,
        description="是否顯示 SQL 查詢語句（開發用）"
    )

    # API 伺服器設定
    HOST: str = Field(default="0.0.0.0", description="伺服器 Host")
    PORT: int = Field(default=8000, description="伺服器 Port")

    # CORS 設定
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="允許的 CORS 來源（逗號分隔）"
    )

    # OpenAI API 設定
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API 金鑰"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-3.5-turbo",
        description="使用的 OpenAI 模型"
    )
    USE_MOCK_AI: bool = Field(
        default=False,
        description="使用 Mock AI（開發測試用，不需要 OpenAI API Key）"
    )

    # 爬蟲設定
    RATE_LIMIT_PER_SECOND: float = Field(
        default=1.0,
        description="爬蟲請求速率限制（每秒請求數）"
    )
    USER_AGENT: str = Field(
        default="VibeCodingNoteBot/1.0",
        description="爬蟲 User-Agent"
    )
    SCRAPER_TIMEOUT: int = Field(
        default=30,
        description="爬蟲請求超時時間（秒）"
    )

    # 資料保留設定
    DATA_RETENTION_DAYS: int = Field(
        default=30,
        description="資料保留天數"
    )

    # 版本控制設定
    MAX_VERSIONS_PER_DOCUMENT: int = Field(
        default=50,
        description="每份文件保留的最大版本數"
    )

    # 文字相似度設定
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        description="文字相似度閾值（超過視為抄襲）"
    )

    # 內容品質設定
    QUALITY_SCORE_THRESHOLD: float = Field(
        default=60.0,
        description="Block 品質評分閾值（低於此值不保留）"
    )

    # 開發模式設定
    DEBUG: bool = Field(
        default=False,
        description="是否為開發模式"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """將 CORS_ORIGINS 字串轉換為列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """是否為生產環境"""
        return not self.DEBUG and not self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # 環境變數不區分大小寫


# 全域設定實例
settings = Settings()


def get_settings() -> Settings:
    """
    FastAPI dependency: 取得設定實例

    使用方式：
        @app.get("/config")
        def get_config(settings: Settings = Depends(get_settings)):
            return {"database": settings.DATABASE_URL}
    """
    return settings

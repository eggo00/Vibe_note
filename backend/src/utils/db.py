"""
資料庫連線模組
提供 SQLAlchemy engine 與 session 管理
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path

# 從環境變數讀取資料庫 URL，預設使用 SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vibe_note.db")

# SQLite 特殊配置：使用 StaticPool 避免多執行緒問題
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"  # 開發時可設為 true
    )
else:
    # PostgreSQL 或其他資料庫使用預設配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # 連線前測試，避免連線失效
        echo=os.getenv("SQL_ECHO", "false").lower() == "true"
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: 提供資料庫 session
    使用 yield 確保 session 會被正確關閉

    使用方式：
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    初始化資料庫：建立所有資料表
    僅在開發/測試環境使用，生產環境應使用 Alembic migrations
    """
    # 確保資料庫檔案所在目錄存在 (SQLite)
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    # 匯入所有 models 確保它們被註冊
    from ..models import document, data_source, style_profile, export_job  # noqa

    # 建立所有資料表
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    刪除所有資料表 (危險操作！僅供測試使用)
    """
    Base.metadata.drop_all(bind=engine)

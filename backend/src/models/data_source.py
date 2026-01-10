"""
DataSource 與 Block Models
對應 data-model.md §3, §4
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..utils.db import Base


class DataSource(Base):
    """資料來源（Notion, Blog, GitHub）"""
    __tablename__ = "data_sources"

    source_id = Column(String, primary_key=True)  # UUID v4
    document_id = Column(String, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=True)  # 可為 None（匯入時尚未關聯文件）
    source_type = Column(String, nullable=False)  # 'notion' | 'blog' | 'github'
    url = Column(String, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    raw_content_snapshot = Column(Text, nullable=True)  # JSON 格式原始內容
    quality_score = Column(Float, nullable=True)  # 整體品質評分（0-100，僅 Notion）
    meta_data = Column(Text, nullable=True)  # 額外資訊 JSON (改名避免與 SQLAlchemy 保留字衝突)

    # Relationships
    document = relationship("Document", back_populates="data_sources")
    blocks = relationship("Block", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<DataSource(id={self.source_id}, type={self.source_type}, url={self.url})>"


class Block(Base):
    """Notion 內容區塊（block-level）"""
    __tablename__ = "blocks"

    block_id = Column(String, primary_key=True)  # Notion block_id 或自生成 UUID
    source_id = Column(String, ForeignKey("data_sources.source_id", ondelete="CASCADE"), nullable=False)
    block_type = Column(String, nullable=False)  # 'heading' | 'paragraph' | 'code' | 'list' | 'callout' | 'image'
    text_content = Column(Text, nullable=True)
    code_language = Column(String, nullable=True)  # 程式碼語言（block_type='code' 時）
    hierarchy_level = Column(Integer, default=0)  # 標題層級（1=h1, 2=h2, ...）
    position_index = Column(Integer, nullable=False)  # 區塊在頁面中的順序
    quality_score = Column(Float, nullable=False)  # Block 品質評分（0-100）

    # Relationships
    source = relationship("DataSource", back_populates="blocks")

    def __repr__(self) -> str:
        return f"<Block(id={self.block_id}, type={self.block_type}, score={self.quality_score})>"

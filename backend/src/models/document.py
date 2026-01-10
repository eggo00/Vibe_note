"""
Document 與 Version Models
對應 data-model.md §1, §2
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..utils.db import Base


class Document(Base):
    """筆記文件主表"""
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True)  # UUID v4
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # 當前版本的 Markdown 內容
    current_version_id = Column(String, ForeignKey("versions.version_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = relationship("Version", back_populates="document", foreign_keys="Version.document_id", cascade="all, delete-orphan")
    data_sources = relationship("DataSource", back_populates="document", cascade="all, delete-orphan")
    export_jobs = relationship("ExportJob", back_populates="document", cascade="all, delete-orphan")
    current_version = relationship("Version", foreign_keys=[current_version_id], post_update=True)

    def __repr__(self) -> str:
        return f"<Document(id={self.document_id}, title={self.title})>"


class Version(Base):
    """版本歷史（完整快照模式）"""
    __tablename__ = "versions"

    version_id = Column(String, primary_key=True)  # UUID v4
    document_id = Column(String, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)  # 完整 Markdown 內容快照
    created_at = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=False)
    preview = Column(Text, nullable=True)  # 前 50 字預覽

    # Relationships
    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])

    def __repr__(self) -> str:
        return f"<Version(id={self.version_id}, document_id={self.document_id}, current={self.is_current})>"

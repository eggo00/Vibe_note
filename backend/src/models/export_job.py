"""
ExportJob Model
對應 data-model.md §6
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..utils.db import Base


class ExportJob(Base):
    """匯出任務記錄"""
    __tablename__ = "export_jobs"

    job_id = Column(String, primary_key=True)  # UUID v4
    document_id = Column(String, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    format = Column(String, nullable=False)  # 'markdown' | 'html' | 'pdf'
    status = Column(String, default="pending")  # 'pending' | 'processing' | 'completed' | 'failed'
    file_path = Column(String, nullable=True)  # 匯出檔案路徑
    error_message = Column(Text, nullable=True)  # 錯誤訊息（若失敗）
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="export_jobs")

    def __repr__(self) -> str:
        return f"<ExportJob(id={self.job_id}, format={self.format}, status={self.status})>"

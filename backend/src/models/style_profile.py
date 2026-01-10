"""
StyleProfile Model
對應 data-model.md §5
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from ..utils.db import Base


class StyleProfile(Base):
    """寫作風格模型（從老師 Blog 分析）"""
    __tablename__ = "style_profiles"

    profile_id = Column(String, primary_key=True)  # UUID v4
    name = Column(String, nullable=False)  # 風格名稱
    source_urls = Column(Text, nullable=False)  # JSON 陣列：來源 URLs
    common_heading_patterns = Column(Text, nullable=True)  # JSON 陣列：常見標題模式
    paragraph_order = Column(Text, nullable=True)  # JSON 陣列：段落順序模式
    teaching_tone = Column(Text, nullable=True)  # JSON：教學語氣特徵
    code_explanation_style = Column(Text, nullable=True)  # JSON：程式碼解說風格
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(Text, nullable=True)  # JSON：額外資訊 (改名避免與 SQLAlchemy 保留字衝突)

    def __repr__(self) -> str:
        return f"<StyleProfile(id={self.profile_id}, name={self.name})>"

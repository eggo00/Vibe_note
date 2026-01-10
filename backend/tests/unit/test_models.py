"""
Models 基本驗證測試
確保 SQLAlchemy Models 可正確建立與序列化
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from src.models import Document, Version, DataSource, Block, StyleProfile, ExportJob
from src.utils.db import Base


@pytest.fixture
def db_session():
    """建立測試用記憶體資料庫"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestDocumentModel:
    """Document Model 測試"""

    def test_create_document(self, db_session):
        """正常情境：建立文件"""
        doc_id = str(uuid.uuid4())
        doc = Document(
            document_id=doc_id,
            title="測試筆記",
            content="# 標題\n內容..."
        )
        db_session.add(doc)
        db_session.commit()

        # 驗證
        saved_doc = db_session.query(Document).filter_by(document_id=doc_id).first()
        assert saved_doc is not None
        assert saved_doc.title == "測試筆記"
        assert saved_doc.content == "# 標題\n內容..."
        assert saved_doc.created_at is not None

    def test_document_repr(self):
        """驗證 __repr__ 輸出"""
        doc = Document(document_id="test-123", title="Test Doc", content="Content")
        assert "test-123" in repr(doc)
        assert "Test Doc" in repr(doc)


class TestVersionModel:
    """Version Model 測試"""

    def test_create_version(self, db_session):
        """正常情境：建立版本"""
        # 先建立 Document
        doc = Document(
            document_id=str(uuid.uuid4()),
            title="測試",
            content="初始內容"
        )
        db_session.add(doc)
        db_session.commit()

        # 建立 Version
        version = Version(
            version_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            content="版本 1 內容",
            is_current=True,
            preview="版本 1 內容..."
        )
        db_session.add(version)
        db_session.commit()

        # 驗證
        saved_version = db_session.query(Version).filter_by(version_id=version.version_id).first()
        assert saved_version is not None
        assert saved_version.document_id == doc.document_id
        assert saved_version.is_current is True

    def test_version_cascade_delete(self, db_session):
        """異常情境：刪除 Document 時級聯刪除 Version"""
        doc = Document(
            document_id=str(uuid.uuid4()),
            title="測試",
            content="內容"
        )
        db_session.add(doc)
        db_session.commit()

        version = Version(
            version_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            content="版本內容",
            is_current=True
        )
        db_session.add(version)
        db_session.commit()

        # 刪除 Document
        db_session.delete(doc)
        db_session.commit()

        # 驗證 Version 也被刪除
        assert db_session.query(Version).filter_by(version_id=version.version_id).first() is None


class TestDataSourceModel:
    """DataSource Model 測試"""

    def test_create_notion_source(self, db_session):
        """正常情境：建立 Notion 資料來源"""
        doc = Document(document_id=str(uuid.uuid4()), title="Test", content="Content")
        db_session.add(doc)
        db_session.commit()

        source = DataSource(
            source_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            source_type="notion",
            url="https://notion.so/test",
            quality_score=75.5,
            meta_data='{"title": "測試頁面"}'
        )
        db_session.add(source)
        db_session.commit()

        # 驗證
        saved_source = db_session.query(DataSource).filter_by(source_id=source.source_id).first()
        assert saved_source is not None
        assert saved_source.source_type == "notion"
        assert saved_source.quality_score == 75.5


class TestBlockModel:
    """Block Model 測試"""

    def test_create_code_block(self, db_session):
        """正常情境：建立程式碼區塊"""
        doc = Document(document_id=str(uuid.uuid4()), title="Test", content="Content")
        source = DataSource(
            source_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            source_type="notion",
            url="https://notion.so/test"
        )
        db_session.add_all([doc, source])
        db_session.commit()

        block = Block(
            block_id=str(uuid.uuid4()),
            source_id=source.source_id,
            block_type="code",
            text_content="function test() { return true; }",
            code_language="javascript",
            position_index=1,
            quality_score=88.0
        )
        db_session.add(block)
        db_session.commit()

        # 驗證
        saved_block = db_session.query(Block).filter_by(block_id=block.block_id).first()
        assert saved_block is not None
        assert saved_block.block_type == "code"
        assert saved_block.code_language == "javascript"
        assert saved_block.quality_score == 88.0

    def test_high_quality_blocks_filter(self, db_session):
        """業務規則驗證：篩選 quality_score >= 60 的 blocks"""
        doc = Document(document_id=str(uuid.uuid4()), title="Test", content="Content")
        source = DataSource(
            source_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            source_type="notion",
            url="https://notion.so/test"
        )
        db_session.add_all([doc, source])
        db_session.commit()

        # 建立 3 個 blocks：高品質 (85, 70) 和低品質 (45)
        blocks = [
            Block(block_id=str(uuid.uuid4()), source_id=source.source_id, block_type="paragraph",
                  text_content="高品質內容 1", position_index=0, quality_score=85.0),
            Block(block_id=str(uuid.uuid4()), source_id=source.source_id, block_type="paragraph",
                  text_content="高品質內容 2", position_index=1, quality_score=70.0),
            Block(block_id=str(uuid.uuid4()), source_id=source.source_id, block_type="paragraph",
                  text_content="低品質內容", position_index=2, quality_score=45.0),
        ]
        db_session.add_all(blocks)
        db_session.commit()

        # 篩選 quality_score >= 60
        high_quality = db_session.query(Block).filter(Block.quality_score >= 60).all()
        assert len(high_quality) == 2


class TestStyleProfileModel:
    """StyleProfile Model 測試"""

    def test_create_style_profile(self, db_session):
        """正常情境：建立風格檔案"""
        profile = StyleProfile(
            profile_id=str(uuid.uuid4()),
            name="老師 Blog 風格",
            source_urls='["https://blog.com/post1", "https://blog.com/post2"]',
            common_heading_patterns='["## 核心概念", "## 實作步驟"]',
            meta_data='{"article_count": 5}'
        )
        db_session.add(profile)
        db_session.commit()

        # 驗證
        saved_profile = db_session.query(StyleProfile).filter_by(profile_id=profile.profile_id).first()
        assert saved_profile is not None
        assert saved_profile.name == "老師 Blog 風格"
        assert "blog.com" in saved_profile.source_urls


class TestExportJobModel:
    """ExportJob Model 測試"""

    def test_create_export_job(self, db_session):
        """正常情境：建立匯出任務"""
        doc = Document(document_id=str(uuid.uuid4()), title="Test", content="Content")
        db_session.add(doc)
        db_session.commit()

        job = ExportJob(
            job_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            format="pdf",
            status="pending"
        )
        db_session.add(job)
        db_session.commit()

        # 驗證
        saved_job = db_session.query(ExportJob).filter_by(job_id=job.job_id).first()
        assert saved_job is not None
        assert saved_job.format == "pdf"
        assert saved_job.status == "pending"

    def test_export_job_status_update(self, db_session):
        """正常情境：更新匯出任務狀態"""
        doc = Document(document_id=str(uuid.uuid4()), title="Test", content="Content")
        job = ExportJob(
            job_id=str(uuid.uuid4()),
            document_id=doc.document_id,
            format="markdown",
            status="pending"
        )
        db_session.add_all([doc, job])
        db_session.commit()

        # 更新狀態
        job.status = "completed"
        job.file_path = "/tmp/exports/note.md"
        job.completed_at = datetime.utcnow()
        db_session.commit()

        # 驗證
        saved_job = db_session.query(ExportJob).filter_by(job_id=job.job_id).first()
        assert saved_job.status == "completed"
        assert saved_job.file_path == "/tmp/exports/note.md"
        assert saved_job.completed_at is not None

#!/usr/bin/env python3
"""
資料庫初始化腳本
執行 data-model.md 中定義的 SQL schema
"""

import sqlite3
import os
from pathlib import Path

# 資料庫檔案路徑
DB_PATH = Path(__file__).parent.parent / "vibe_note.db"

# SQL Schema (from data-model.md)
SCHEMA_SQL = """
-- 1. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    current_version_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_document_updated ON documents(updated_at DESC);

-- 2. Versions Table
CREATE TABLE IF NOT EXISTS versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    preview TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_version_document ON versions(document_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_version_current ON versions(document_id, is_current);

-- 3. DataSources Table
CREATE TABLE IF NOT EXISTS data_sources (
    source_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    url TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_content_snapshot TEXT,
    quality_score REAL,
    metadata TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_source_document ON data_sources(document_id);
CREATE INDEX IF NOT EXISTS idx_source_type ON data_sources(source_type);

-- 4. Blocks Table
CREATE TABLE IF NOT EXISTS blocks (
    block_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    block_type TEXT NOT NULL,
    text_content TEXT,
    code_language TEXT,
    hierarchy_level INTEGER DEFAULT 0,
    position_index INTEGER NOT NULL,
    quality_score REAL NOT NULL,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_block_source ON blocks(source_id, position_index);
CREATE INDEX IF NOT EXISTS idx_block_quality ON blocks(quality_score DESC);

-- 5. StyleProfiles Table
CREATE TABLE IF NOT EXISTS style_profiles (
    profile_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source_urls TEXT NOT NULL,
    common_heading_patterns TEXT,
    paragraph_order TEXT,
    teaching_tone TEXT,
    code_explanation_style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_profile_name ON style_profiles(name);

-- 6. ExportJobs Table
CREATE TABLE IF NOT EXISTS export_jobs (
    job_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    format TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    file_path TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_export_document ON export_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_export_status ON export_jobs(status);
"""


def init_database():
    """初始化資料庫"""
    print(f"初始化資料庫: {DB_PATH}")

    # 如果資料庫已存在，詢問是否覆蓋
    if DB_PATH.exists():
        response = input(f"資料庫 {DB_PATH} 已存在。是否覆蓋? (y/N): ")
        if response.lower() != 'y':
            print("取消初始化")
            return
        os.remove(DB_PATH)
        print("已刪除舊資料庫")

    # 建立連線並執行 schema
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        print("✓ 資料庫初始化成功")

        # 顯示建立的資料表
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ 已建立 {len(tables)} 個資料表:")
        for table in tables:
            print(f"  - {table}")

    except Exception as e:
        print(f"✗ 錯誤: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()

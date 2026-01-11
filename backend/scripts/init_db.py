"""
資料庫初始化腳本
建立所有資料表
"""
import sys
from pathlib import Path

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.db import init_db, Base, engine


def main():
    """初始化資料庫"""
    print("=" * 50)
    print("🗄️  初始化資料庫...")
    print("=" * 50)

    try:
        # 建立所有資料表
        init_db()

        print("\n✅ 資料庫初始化成功！")
        print("\n建立的資料表：")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"\n❌ 資料庫初始化失敗：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Pytest 配置檔案
提供共用的 fixtures 與測試設定
"""
import sys
from pathlib import Path

# 將 src 目錄加入 Python path，讓測試可以 import 專案模組
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

"""
FastAPI 主應用程式
對應 tasks.md T021
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api import health
from .api import notion
from .api import analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # Startup
    print("=" * 50)
    print("🚀 Vibe Note API 啟動中...")
    print(f"📊 資料庫: {settings.DATABASE_URL}")
    print(f"🌐 CORS 允許來源: {', '.join(settings.cors_origins_list)}")
    print(f"🔧 環境: {'Production' if settings.is_production else 'Development'}")
    print(f"📖 API 文件: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 50)

    yield

    # Shutdown
    print("\n👋 Vibe Note API 關閉中...")


# 建立 FastAPI 應用
app = FastAPI(
    title="Vibe Note API",
    description="AI 驅動的學習筆記自動生成系統",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan
)

# CORS 設定（允許前端跨域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # 從環境變數載入
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 Headers
)

# 註冊路由
app.include_router(health.router)
app.include_router(notion.router)
app.include_router(analyze.router)


# 根路徑重定向到 API 文件
@app.get("/", include_in_schema=False)
def root():
    """根路徑重定向到 Swagger UI"""
    return {
        "message": "Vibe Note API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

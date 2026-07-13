"""TaleForge 主应用入口。"""

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
import os

from backend.routers import story_router, history_router, config_router, works_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="TaleForge - 智能故事生成器", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story_router, prefix="/api/v1/story", tags=["故事"])
app.include_router(history_router, prefix="/api/v1/history", tags=["历史"])
app.include_router(config_router, prefix="/api/v1/config", tags=["配置"])
app.include_router(works_router, prefix="/api/v1/works", tags=["作品"])


@app.get("/api/v1/health")
async def health_check():
    """健康检查接口。"""
    return {"status": "healthy", "service": "TaleForge", "version": "1.0.0"}


frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
assets_dir = os.path.join(frontend_dir, "assets")
components_dir = os.path.join(frontend_dir, "components")

if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

if os.path.exists(components_dir):
    app.mount("/components", StaticFiles(directory=components_dir), name="components")


@app.get("/")
async def serve_index():
    """服务前端首页。"""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Index file not found"}


@app.get("/favicon.ico")
async def favicon():
    """返回空 favicon 避免 404 错误。"""
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT
    uvicorn.run(app, host=HOST, port=PORT)
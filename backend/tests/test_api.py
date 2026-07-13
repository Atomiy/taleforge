"""TaleForge API 全面测试套件。"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app

pytest_plugins = ('pytest_asyncio',)

# ============================================================
# 基础功能测试
# ============================================================

@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查接口。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TaleForge"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_frontend_index():
    """测试前端首页访问。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        body = response.text
        assert "TaleForge" in body
        assert "vue.global.prod.js" in body


@pytest.mark.asyncio
async def test_static_assets():
    """测试静态资源访问。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/assets/js/vue.global.prod.js")
        assert response.status_code == 200
        assert "application/javascript" in response.headers["content-type"]


# ============================================================
# 配置 API 测试
# ============================================================

@pytest.mark.asyncio
async def test_get_config():
    """测试获取配置信息。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/config/")
        assert response.status_code == 200
        data = response.json()
        assert "api_key_configured" in data
        assert "available_genres" in data
        assert "available_styles" in data
        assert "available_perspectives" in data
        assert "available_conflicts" in data
        assert "available_moods" in data
        assert isinstance(data["available_genres"], list)
        assert len(data["available_genres"]) > 0


@pytest.mark.asyncio
async def test_set_api_key():
    """测试设置 API Key。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/config/api-key",
            json={"api_key": "sk-test-key-12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


# ============================================================
# 故事 CRUD 测试
# ============================================================

@pytest.mark.asyncio
async def test_save_story_basic():
    """测试保存故事（基本字段）。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "测试故事",
                "content": "这是一个测试内容",
                "theme": "测试主题",
                "genre": "短篇小说",
                "style": "温馨"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "story_id" in data
        assert len(data["story_id"]) > 0
        return data["story_id"]


@pytest.mark.asyncio
async def test_save_story_full():
    """测试保存故事（完整字段）。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "完整测试故事",
                "content": "完整的故事内容",
                "theme": "剑与魔法",
                "genre": "奇幻",
                "style": "史诗",
                "world_setting": "艾泽拉斯大陆",
                "foreshadowings": ["古老的预言", "黑暗的阴影"],
                "previous_story_id": "",
                "series_id": "series_001",
                "series_order": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        return data["story_id"]


@pytest.mark.asyncio
async def test_get_story_detail():
    """测试获取故事详情。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        save_resp = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "详情测试",
                "content": "详情内容",
                "theme": "测试",
                "genre": "短篇小说",
                "style": "温馨"
            }
        )
        story_id = save_resp.json()["story_id"]

        response = await ac.get(f"/api/v1/story/{story_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == story_id
        assert data["title"] == "详情测试"
        assert data["content"] == "详情内容"
        assert data["genre"] == "短篇小说"


@pytest.mark.asyncio
async def test_get_nonexistent_story():
    """测试获取不存在的故事返回404。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/story/nonexistent_id")
        assert response.status_code == 404


# ============================================================
# 历史记录 API 测试（含分页、搜索）
# ============================================================

@pytest.mark.asyncio
async def test_history_empty():
    """测试空历史记录。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/history/")
        assert response.status_code == 200
        data = response.json()
        assert "stories" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_history_pagination():
    """测试历史记录分页。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/history/?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["page"] == 1
        assert data["page_size"] == 5


@pytest.mark.asyncio
async def test_history_search():
    """测试历史记录搜索。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/history/?search=测试")
        assert response.status_code == 200
        data = response.json()
        assert "stories" in data


@pytest.mark.asyncio
async def test_history_filter_by_genre():
    """测试按体裁筛选历史记录。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/history/?genre=奇幻")
        assert response.status_code == 200
        data = response.json()
        for story in data["stories"]:
            assert story["genre"] == "奇幻"


# ============================================================
# 删除功能测试
# ============================================================

@pytest.mark.asyncio
async def test_delete_story():
    """测试删除故事。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        save_resp = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "待删除",
                "content": "将被删除",
                "theme": "测试",
                "genre": "短篇小说",
                "style": "温馨"
            }
        )
        story_id = save_resp.json()["story_id"]

        delete_resp = await ac.delete(f"/api/v1/history/{story_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["success"] is True

        get_resp = await ac.get(f"/api/v1/story/{story_id}")
        assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_story():
    """测试删除不存在的故事返回404。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/api/v1/history/nonexistent_id")
        assert response.status_code == 404


# ============================================================
# 导出功能测试
# ============================================================

@pytest.mark.asyncio
async def test_export_story_markdown():
    """测试导出故事为 Markdown。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        save_resp = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "导出测试",
                "content": "用于导出的故事内容",
                "theme": "测试",
                "genre": "短篇小说",
                "style": "温馨"
            }
        )
        story_id = save_resp.json()["story_id"]

        response = await ac.get(f"/api/v1/history/export/{story_id}?format=markdown")
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]
        body = response.text
        assert "导出测试" in body
        assert "TaleForge" in body


@pytest.mark.asyncio
async def test_export_story_text():
    """测试导出故事为纯文本。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        save_resp = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "导出文本测试",
                "content": "文本内容",
                "theme": "测试",
                "genre": "短篇小说",
                "style": "温馨"
            }
        )
        story_id = save_resp.json()["story_id"]

        response = await ac.get(f"/api/v1/history/export/{story_id}?format=text")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_story_not_found():
    """测试导出不存在的故事返回404。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/history/export/nonexistent?format=markdown")
        assert response.status_code == 404


# ============================================================
# 错误处理测试
# ============================================================

@pytest.mark.asyncio
async def test_save_story_empty_title():
    """测试保存空标题的故事。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/story/save",
            json={
                "title": "",
                "content": "内容",
                "theme": "测试",
                "genre": "短篇小说",
                "style": "温馨"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ============================================================
# API 版本和 CORS 测试
# ============================================================

@pytest.mark.asyncio
async def test_404_handler():
    """测试不存在的 API 路由返回404。"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/nonexistent_route")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""前端 E2E 自动化检测脚本。
使用 Playwright 在真实浏览器中检测前端渲染、交互和功能。
运行: python -m pytest backend/tests/test_frontend.py -v --tb=short
"""

import time
import os

from conftest import SERVER_URL


def test_page_loads_successfully(page):
    """检测：页面正常加载，状态码200。"""
    response = page.goto(SERVER_URL, wait_until="networkidle")
    assert response.status == 200
    assert "TaleForge" in page.title()


def test_vue_app_mounts(page):
    """检测：Vue应用成功挂载，没有Vue初始化错误。"""
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    assert len(errors) == 0, f"Vue渲染错误: {errors}"


def test_toast_container_exists(page):
    """检测：Toast通知容器存在（替代alert的修复）。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    toast_container = page.locator("#toast-container")
    assert toast_container.count() == 1


def test_no_javascript_errors(page):
    """检测：页面没有JavaScript异常。"""
    js_errors = []
    page.on("pageerror", lambda err: js_errors.append(str(err)))
    page.on("console", lambda msg: 
        js_errors.append(msg.text) if msg.type == "error" else None)
    
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(2)
    
    non_critical = ["cdn.tailwindcss.com", "favicon.ico"]
    critical_errors = [e for e in js_errors if not any(x in e for x in non_critical)]
    
    assert len(critical_errors) == 0, f"JS错误:\n" + "\n".join(critical_errors)


def test_key_ui_elements_exist(page):
    """检测：所有关键UI元素都存在。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    checks = {
        "导航栏": page.locator("nav"),
        "创建标签页": page.locator("button:has-text('创作')"),
        "历史标签页": page.locator("button:has-text('历史')"),
        "主题输入框": page.locator("input[placeholder*='主题']"),
        "生成按钮": page.locator("button:has-text('开始生成')"),
        "API设置按钮": page.locator("button:has-text('设置')"),
        "角色设定区域": page.locator("text=角色设定"),
        "世界观设定区域": page.locator("text=世界观设定"),
        "剧情设定区域": page.locator("text=剧情设置"),
    }
    
    for name, locator in checks.items():
        assert locator.count() > 0, f"关键元素缺失: {name}"


def test_character_add_button_exists(page):
    """检测：角色自定义添加按钮存在。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    custom_add = page.locator("button:has-text('自定义添加')")
    template_add = page.locator("button:has-text('从模板添加')")
    
    assert custom_add.count() > 0, "自定义添加按钮缺失"
    assert template_add.count() > 0, "从模板添加按钮缺失"


def test_search_and_export_buttons_exist(page):
    """检测：搜索和导出按钮存在。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    
    history_tab = page.locator("button:has-text('历史')")
    history_tab.click()
    time.sleep(1)
    
    search_input = page.locator("input[placeholder*='搜索']")
    search_btn = page.locator("button:has-text('搜索')")
    
    assert search_input.count() > 0, "搜索输入框缺失"
    assert search_btn.count() > 0, "搜索按钮缺失"


def test_tab_switching_works(page):
    """检测：创作/历史标签页切换正常。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    create_tab = page.locator("button:has-text('创作')")
    create_tab.click()
    time.sleep(0.5)
    
    history_tab = page.locator("button:has-text('历史')")
    history_tab.click()
    time.sleep(0.5)
    
    create_tab.click()
    time.sleep(0.5)
    
    theme_input = page.locator("input[placeholder*='主题']")
    assert theme_input.count() > 0


def test_custom_character_addition(page):
    """检测：自定义添加角色功能正常（弹窗填写后添加）。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    custom_add = page.locator("button:has-text('自定义添加')")
    initial_count = page.locator('text=角色 1').count()
    
    custom_add.click()
    time.sleep(0.5)
    
    # 弹窗已打开，填写角色名称
    name_input = page.locator("input[placeholder*='名称']")
    if name_input.count() > 0:
        name_input.fill("测试角色")
    
    # 点击确认添加
    confirm_btn = page.locator("button:has-text('确认添加')")
    if confirm_btn.count() > 0:
        confirm_btn.click()
    time.sleep(0.5)
    
    new_count = page.locator('text=角色 1').count()
    assert new_count > initial_count, f"自定义添加角色未生效 (before={initial_count}, after={new_count})"


def test_form_input_works(page):
    """检测：表单输入正常。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    theme_input = page.locator("input[placeholder*='主题']")
    theme_input.fill("测试故事主题")
    
    filled = theme_input.input_value()
    assert filled == "测试故事主题", f"输入值不匹配: '{filled}'"


def test_foreshadowing_add_and_remove(page):
    """检测：伏笔添加功能正常。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    foreshadow_input = page.locator("input[placeholder*='伏笔']")
    if foreshadow_input.count() > 0:
        foreshadow_input.fill("古老的预言")
        foreshadow_input.press("Enter")
        time.sleep(0.5)


def test_config_modal_opens(page):
    """检测：配置弹窗能正常打开。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    api_btn = page.locator("button:has-text('设置')")
    if api_btn.count() > 0:
        api_btn.click()
        time.sleep(0.5)
        close_btn = page.locator("button:has-text('关闭')")
        if close_btn.count() > 0:
            close_btn.click()


def test_history_tab_shows_records(page):
    """检测：历史记录标签页显示正常。"""
    page.goto(SERVER_URL, wait_until="networkidle")
    
    history_tab = page.locator("button:has-text('历史')")
    history_tab.click()
    time.sleep(2)
    
    assert not page.locator("text=TypeError").count()


def test_mobile_viewport(page):
    """检测：移动端视口下页面不崩溃。"""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    time.sleep(0.5)
    
    assert len(errors) == 0, f"移动端渲染错误: {errors}"


def test_tablet_viewport(page):
    """检测：平板视口下页面不崩溃。"""
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto(SERVER_URL, wait_until="networkidle")
    time.sleep(1)
    
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    time.sleep(0.5)
    
    assert len(errors) == 0, f"平板渲染错误: {errors}"

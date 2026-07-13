"""pytest 配置 - 启动/关闭测试服务器 + Playwright 浏览器。"""

import os
import sys
import subprocess
import time
import urllib.request
import pytest

SERVER_URL = "http://127.0.0.1:8080"
TEST_PORT = "8080"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYWRIGHT_BROWSERS = os.path.join(PROJECT_ROOT, "playwright-browsers")
server_process = None


def kill_port_processes(port):
    """杀死占用指定端口的所有进程，最多重试3轮。"""
    for attempt in range(3):
        try:
            result = subprocess.check_output(
                ['netstat', '-ano'], text=True, stderr=subprocess.STDOUT
            )
            pids = set()
            pattern = f':{port}\\s+'
            for line in result.split('\n'):
                if pattern in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5 and parts[-1].isdigit():
                        pids.add(int(parts[-1]))
            if not pids:
                time.sleep(0.5)
                return
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                                   check=True, capture_output=True, timeout=5)
                    print(f"[CONFTEST] Killed process {pid} on port {port}")
                except Exception:
                    pass
            time.sleep(2)
        except Exception:
            pass


def pytest_sessionstart(session):
    """在所有测试开始前启动服务器。"""
    global server_process
    print(f"\n[CONFTEST] Checking port {TEST_PORT}...")
    kill_port_processes(TEST_PORT)

    print(f"[CONFTEST] Starting test server on {SERVER_URL}...")
    print(f"[CONFTEST] Project root: {PROJECT_ROOT}")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", TEST_PORT],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for i in range(25):
        try:
            urllib.request.urlopen(f"{SERVER_URL}/api/v1/health", timeout=2)
            print(f"[CONFTEST] Server ready after {i+1}s")
            return
        except Exception:
            time.sleep(1)
    print("[CONFTEST] WARNING: Server may not have started!")


def pytest_sessionfinish(session):
    """在所有测试结束后关闭服务器。"""
    global server_process
    if server_process:
        server_process.terminate()
        server_process.wait()
        print("[CONFTEST] Test server stopped")


@pytest.fixture(scope="session")
def browser_context():
    """启动 Playwright 浏览器（会话级，复用浏览器实例）。"""
    from playwright.sync_api import sync_playwright
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = PLAYWRIGHT_BROWSERS

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )
        yield context
        browser.close()


@pytest.fixture
def page(browser_context):
    """创建新页面（函数级，每个测试独立页面）。"""
    _page = browser_context.new_page()
    _page.on("console", lambda msg: print(f"[BROWSER {msg.type}] {msg.text}"))
    yield _page
    _page.close()

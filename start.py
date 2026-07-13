#!/usr/bin/env python
"""TaleForge 启动器 - 一键设置环境、安装依赖、配置API密钥并启动服务器。"""

import os
import sys
import subprocess
import time
import socket
import re

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_DIR, "venv")
REQUIREMENTS_FILE = os.path.join(PROJECT_DIR, "requirements.txt")
ENV_FILE = os.path.join(PROJECT_DIR, ".env")
ENV_EXAMPLE_FILE = os.path.join(PROJECT_DIR, ".env.example")


def get_venv_python():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def get_venv_pip():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def read_env_value(key):
    if not os.path.exists(ENV_FILE):
        return ""
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    return ""


def write_env_value(key, value):
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if f"{key}=" in content:
            pattern = re.compile(rf"^{re.escape(key)}=.*$", re.MULTILINE)
            content = pattern.sub(f"{key}={value}", content)
        else:
            content = content.rstrip() + f"\n{key}={value}\n"
    else:
        content = f"{key}={value}\n"
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def print_banner():
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║       TaleForge - AI Story Generator      ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()


def step(msg):
    print(f"  >> {msg}")


def ok(msg):
    print(f"  [OK] {msg}")


def warn(msg):
    print(f"  [WARN] {msg}")


def fail(msg):
    print(f"  [ERROR] {msg}")


def check_venv():
    python_exe = get_venv_python()
    if os.path.exists(python_exe):
        try:
            result = subprocess.run(
                [python_exe, "-c", "print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            if "ok" in result.stdout:
                return True
        except Exception:
            pass
    return False


def setup_venv():
    step("Setting up Python virtual environment...")
    try:
        if os.path.exists(VENV_DIR):
            import shutil
            shutil.rmtree(VENV_DIR, ignore_errors=True)
        subprocess.run(
            [sys.executable, "-m", "venv", VENV_DIR],
            check=True, capture_output=True, text=True
        )
        ok("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        fail(f"Failed to create virtual environment: {e.stderr}")
        return False


def install_dependencies():
    pip_exe = get_venv_pip()
    if not os.path.exists(pip_exe):
        fail("pip not found in virtual environment")
        return False

    step("Installing project dependencies...")
    try:
        result = subprocess.run(
            [pip_exe, "install", "-r", REQUIREMENTS_FILE],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            ok("Dependencies installed successfully")
            return True
        else:
            fail(f"Dependency installation failed:\n{result.stderr[-500:]}")
            return False
    except Exception as e:
        fail(f"Dependency installation error: {e}")
        return False


def ensure_dependencies():
    pip_exe = get_venv_pip()
    if not os.path.exists(pip_exe):
        return False

    required = ["fastapi", "uvicorn", "pydantic", "requests", "dotenv", "sseclient"]
    missing = []
    for pkg in required:
        try:
            result = subprocess.run(
                [pip_exe, "show", pkg],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                missing.append(pkg)
        except Exception:
            missing.append(pkg)

    if missing:
        step(f"Missing packages: {', '.join(missing)}")
        return install_dependencies()
    else:
        ok("All dependencies found")
        return True


def ensure_env_file():
    api_key = read_env_value("DEEPSEEK_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        if not os.path.exists(ENV_FILE) and os.path.exists(ENV_EXAMPLE_FILE):
            import shutil
            shutil.copy(ENV_EXAMPLE_FILE, ENV_FILE)

        print()
        print("  ╔═══════════════════════════════════════════╗")
        print("  ║       配置 DeepSeek API Key               ║")
        print("  ╠═══════════════════════════════════════════╣")
        print("  ║  请在下方输入你的 DeepSeek API Key        ║")
        print("  ║  获取地址: https://platform.deepseek.com  ║")
        print("  ║  (直接按回车跳过，稍后可在设置中配置)     ║")
        print("  ╚═══════════════════════════════════════════╝")
        print()

        try:
            new_key = input("  API Key: ").strip()
        except (EOFError, KeyboardInterrupt):
            new_key = ""

        if new_key:
            write_env_value("DEEPSEEK_API_KEY", new_key)
            ok("API Key saved to .env file")
        else:
            warn("No API Key provided. Please configure it in settings after startup.")

    api_key = read_env_value("DEEPSEEK_API_KEY")
    if api_key and api_key != "your_api_key_here":
        masked = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
        ok(f"API Key configured: {masked}")
    else:
        warn("API Key not configured. The app will start but cannot generate stories.")


def get_processes_on_port(port):
    pids = set()
    try:
        import psutil
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                pids.add(conn.pid)
    except ImportError:
        pass

    if not pids:
        try:
            result = subprocess.check_output(
                ['netstat', '-ano'], text=True, stderr=subprocess.STDOUT
            )
            for line in result.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if parts and parts[-1].isdigit():
                        pids.add(int(parts[-1]))
        except Exception:
            pass
    return list(pids)


def kill_process(pid):
    try:
        if sys.platform == "win32":
            subprocess.run(
                ['taskkill', '/F', '/PID', str(pid), '/T'],
                check=True, capture_output=True, timeout=5
            )
        else:
            subprocess.run(
                ['kill', '-9', str(pid)],
                check=True, capture_output=True, timeout=5
            )
        return True
    except Exception:
        return False


def kill_port_processes(port):
    for attempt in range(3):
        pids = get_processes_on_port(port)
        if not pids:
            time.sleep(0.5)
            if not get_processes_on_port(port):
                return True

        print(f"  ║  Found {len(pids)} process(es) on port {port}: {pids}")
        for pid in pids:
            if kill_process(pid):
                print(f"  ║  Killed process {pid}")
            else:
                print(f"  ║  Failed to kill process {pid}")
        time.sleep(2)
    return not get_processes_on_port(port)


def check_port_free(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.connect_ex(('127.0.0.1', port)) != 0
    except Exception:
        return False


def main():
    os.chdir(PROJECT_DIR)
    print_banner()

    host = read_env_value("HOST") or "127.0.0.1"
    try:
        port = int(read_env_value("PORT") or "8080")
    except ValueError:
        port = 8080

    step("Checking environment...")

    if not check_venv():
        step("Virtual environment needs setup")
        if not setup_venv():
            sys.exit(1)

    if not ensure_dependencies():
        fail("Failed to set up dependencies")
        sys.exit(1)

    ensure_env_file()

    print(f"  ║")
    print(f"  ║  Server: http://{host}:{port}")
    print(f"  ║")

    if not check_port_free(port):
        occupied = get_processes_on_port(port)
        print(f"  ║  Port {port} occupied by: {occupied}")
        print(f"  ║  Freeing port {port}...")
        if not kill_port_processes(port):
            fail(f"Cannot free port {port}")
            sys.exit(1)
        ok(f"Port {port} freed")

    print(f"  ║")
    print(f"  ║  Starting TaleForge server...")
    print(f"  ║  Press Ctrl+C to stop")
    print(f"  ║")
    print(f"  ╚═══════════════════════════════════════════╝")
    print()

    python_exe = get_venv_python()
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_DIR + os.pathsep + env.get("PYTHONPATH", "")

    cmd = [
        python_exe, "-m", "uvicorn", "backend.main:app",
        "--host", host, "--port", str(port)
    ]

    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n  ║  Server stopped by user")
    except Exception as e:
        fail(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

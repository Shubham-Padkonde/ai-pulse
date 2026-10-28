"""Start both local services. Ctrl+C stops only these child processes."""

import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
node = shutil.which("node")
if not python.exists() or not node:
    raise SystemExit("Run python scripts/setup.py --demo first.")
flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
processes = []
try:
    processes.append(
        subprocess.Popen(
            [
                str(python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=ROOT / "backend",
            creationflags=flags,
        )
    )
    processes.append(
        subprocess.Popen(
            [
                node,
                "node_modules/vite/bin/vite.js",
                "--host",
                "127.0.0.1",
                "--port",
                "5173",
                "--strictPort",
            ],
            cwd=ROOT / "frontend",
            creationflags=flags,
        )
    )
    print("AI Pulse: http://127.0.0.1:5173 | API: http://127.0.0.1:8000", flush=True)
    while all(p.poll() is None for p in processes):
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopping AI Pulse...", flush=True)
finally:
    for p in processes:
        if p.poll() is None:
            if os.name == "nt":
                # The virtualenv launcher has its own Python child on Windows.
                subprocess.run(
                    ["taskkill", "/PID", str(p.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                p.terminate()
    for p in processes:
        p.wait()

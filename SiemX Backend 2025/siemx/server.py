# server.py
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import Any, Dict, List
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
import sys
import re
from datetime import datetime

# -----------------------------
# In-memory stores
# -----------------------------
ALERTS: List[Dict[str, Any]] = []
LOGS: List[Dict[str, Any]] = []
INSIGHTS: List[str] = []

MAX_ALERTS = 500
MAX_LOGS = 1000
MAX_INSIGHTS = 200

# -----------------------------
# Base dir + log file (RELATIVE)
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
LOG_FILE_PATH = os.path.join(BASE_DIR, "received.log")

# -----------------------------
# Normalizers (map flexible fields to UI shape)
# -----------------------------
def normalize_alert(a: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": a.get("id") or a.get("_id") or f"a-{len(ALERTS)+1}-{int(datetime.utcnow().timestamp())}",
        "timestamp": a.get("timestamp") or a.get("time") or a.get("ts") or datetime.utcnow().isoformat() + "Z",
        "source": a.get("source") or a.get("src") or a.get("ip") or "unknown",
        "destination": a.get("destination") or a.get("dst") or a.get("target") or "unknown",
        "level": a.get("level") or a.get("severity") or "Low",
        "status": a.get("status") or a.get("state") or "Open",
        "action": a.get("action") or a.get("response") or "None",
    }

def normalize_log(l: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": l.get("id") or l.get("_id") or f"l-{len(LOGS)+1}-{int(datetime.utcnow().timestamp())}",
        "timestamp": l.get("timestamp") or l.get("time") or l.get("ts") or datetime.utcnow().isoformat() + "Z",
        "level": l.get("level") or l.get("severity") or "Low",
        "message": l.get("message") or l.get("msg") or "",
    }

# -----------------------------
# Parsing for received.log format
# -----------------------------
LINE_RE = re.compile(
    r"^(?P<timestamp>\S+)\s+\('(?P<ip>[^']+)',\s*(?P<port>\d+)\)\s+\[(?P<state>OPENED|CLOSED|ACTIVE)\]\s+(?P<proc>.+)$"
)

def parse_log_line(line: str) -> Dict[str, Any]:
    m = LINE_RE.match(line)
    if not m:
        return normalize_log({"message": line.strip(), "level": "Low"})
    ts = m.group("timestamp")
    ip = m.group("ip")
    port = m.group("port")
    state = m.group("state")
    proc = m.group("proc")
    if state == "OPENED":
        level = "Medium"
    elif state == "ACTIVE":
        level = "Low"
    else:
        level = "Low"
    msg = f"{proc} {state} from {ip}:{port}"
    return normalize_log({"timestamp": ts, "message": msg, "level": level})

# -----------------------------
# App + CORS
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks: List[asyncio.Task] = []
    log_path = LOG_FILE_PATH  # <<< use relative path

    # Seed last lines so UI shows data immediately
    try:
        seed_last_lines(log_path, max_lines=200)
    except Exception:
        pass

    # Tail in background if the file exists
    if os.path.exists(log_path):
        tasks.append(asyncio.create_task(tail_file(log_path)))

    # If you later want to pipe monitor.py/edr.py stdout, uncomment:
    # tasks.append(asyncio.create_task(run_monitor_subprocess(os.path.join(BASE_DIR, "monitor.py"))))
    # tasks.append(asyncio.create_task(run_edr_subprocess(os.path.join(BASE_DIR, "edr.py"))))

    try:
        yield
    finally:
        for t in tasks:
            t.cancel()
        for t in tasks:
            try:
                await t
            except asyncio.CancelledError:
                pass

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Health + REST Endpoints
# -----------------------------
@app.get("/health")
def health():
    return {"ok": True, "alerts": len(ALERTS), "logs": len(LOGS)}

@app.get("/api/alerts")
def api_alerts():
    return ALERTS

@app.get("/api/logs")
def api_logs():
    return LOGS

@app.get("/api/insights")
def api_insights():
    return INSIGHTS

# -----------------------------
# WebSocket (optional)
# -----------------------------
@app.websocket("/ws")
async def ws_feed(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_text(json.dumps({"alerts": ALERTS, "logs": LOGS, "insights": INSIGHTS}))
        while True:
            await asyncio.sleep(5)
    except Exception:
        pass

# -----------------------------
# Utilities: seed + tailer
# -----------------------------
def seed_last_lines(path: str, max_lines: int = 200):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()[-max_lines:]
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        LOGS.insert(0, parse_log_line(line))
    del LOGS[MAX_LOGS:]

async def tail_file(path: str):
    """Tail received.log and push structured entries into LOGS."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)  # start from end
            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.5)
                    continue
                line = line.strip()
                if not line:
                    continue
                LOGS.insert(0, parse_log_line(line))
                del LOGS[MAX_LOGS:]
    except asyncio.CancelledError:
        return

# -----------------------------
# Optional: pipe monitor.py / edr.py stdout
# -----------------------------
async def run_monitor_subprocess(script_path: str):
    if not os.path.exists(script_path):
        return
    proc = await asyncio.create_subprocess_exec(
        sys.executable, script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=os.path.dirname(script_path),
    )
    try:
        assert proc.stdout is not None
        async for raw in proc.stdout:
            line = raw.decode(errors="ignore").strip()
            if not line:
                continue
            LOGS.insert(0, parse_log_line(line))
            del LOGS[MAX_LOGS:]
    except asyncio.CancelledError:
        proc.terminate()
        try:
            await proc.wait()
        except Exception:
            pass

async def run_edr_subprocess(script_path: str):
    await run_monitor_subprocess(script_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=5000, reload=False)
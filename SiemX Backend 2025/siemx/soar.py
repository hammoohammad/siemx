import time
import json
import re
from datetime import datetime

LOG_FILE = "received.log"
ALERT_FILE = "alerts.txt"

SUSPICIOUS_PROCS = {"cmd.exe", "net.exe", "net1.exe"}
RANSOMWARE_EXTS = {
    ".moka", ".kuub", ".locked", ".bad", ".crypt", ".xyz", ".EncryptedFile",
    ".encrypt", ".crypto", ".virus", ".locker", ".block", ".nolongr", ".crypak",
    ".payms", ".pico", ".shit", ".fuck", ".sensorstechforum", ".sodinokibi",
    ".lilith", ".alice", ".eve", ".doomed", ".ruhr", ".ransom"
}  # Common ransomware file extensions
RENAME_TRACK = {}  # track rapid renames
LOGIN_TRACK = {}  # track recent failed login timestamps per address


LOG_RE = re.compile(
    r"^(?P<ts>[\d\-: ]+),\((?P<addr>[^)]+)\),\[(?P<state>[^\]]+)\]\s*(?P<data>.*)$"
)


def write_alert(ts, source, dest, level, status, action):
    alert = {
        "timestamp": ts,
        "source": source,
        "destination": dest,
        "level": level,
        "status": status,
        "action": action
    }
    with open(ALERT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(alert) + "\n")

    print("[ALERT]", alert)


def is_ransomware_extension(filepath):
    """Check if file has a suspicious ransomware extension"""
    for ext in RANSOMWARE_EXTS:
        if filepath.lower().endswith(ext):
            return True
    return False


def analyze_log(ts, state, data, addr):
    state_u = state.strip().upper()

   
    if state_u == "LOGIN":
        if "failed" in data.lower():
            try:
                t = datetime.fromisoformat(ts.strip())
            except Exception:
                t = datetime.now()

            prev = LOGIN_TRACK.get(addr)
            if prev and (t - prev).total_seconds() <= 60:
                write_alert(
                    ts, addr, "auth",
                    "High", "Bruteforce",
                    "Block IP"
                )
                LOGIN_TRACK.pop(addr, None)
            else:
                LOGIN_TRACK[addr] = t

   
    if state_u == "OPENED" and data.lower().endswith(".exe"):
        proc = data.lower()

        if proc in SUSPICIOUS_PROCS:
            write_alert(
                ts, "process", proc,
                "High", "Detected",
                "Monitor / Investigate"
            )
        else:
            write_alert(
                ts, "process", proc,
                "Low", "Observed",
                "Allow"
            )

  
    if state_u == "CLOSED" and data.lower() in SUSPICIOUS_PROCS:
        write_alert(
            ts, "process", data,
            "Medium", "Closed",
            "Log activity"
        )

  
    if state_u == "FILE CREATED":
        if "$Recycle.Bin" in data:
            write_alert(
                ts, "filesystem", data,
                "Medium", "Suspicious Location",
                "Monitor"
            )
        
        # Check for ransomware extensions
        if is_ransomware_extension(data):
            write_alert(
                ts, "filesystem", data,
                "Critical", "Ransomware Extension Detected",
                "Quarantine Immediately"
            )

    
    if state_u == "FILE RENAMED":
        old, new = data.split(" -> ")
        base = old.split("\\")[-1]

        RENAME_TRACK.setdefault(base, []).append(time.time())

        
        if len(RENAME_TRACK[base]) >= 2:
            write_alert(
                ts, old, new,
                "High", "Multiple Renames",
                "Quarantine File"
            )
        
        # Check if file was renamed to ransomware extension
        if is_ransomware_extension(new):
            write_alert(
                ts, old, new,
                "Critical", "File Renamed to Ransomware Extension",
                "Quarantine Immediately"
            )


def tail_log():
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            line = line.strip()
            if not line:
                continue

            m = LOG_RE.match(line)
            if not m:
                continue

            ts = m.group("ts")
            addr = m.group("addr")
            state = m.group("state")
            data = m.group("data")

            analyze_log(ts, state, data, addr)


if __name__ == "__main__":
    print("[+] Mini SOAR started. Monitoring received.log...")
    tail_log()

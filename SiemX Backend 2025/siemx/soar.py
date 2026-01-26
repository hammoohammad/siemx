import time
import json
import re
from datetime import datetime

LOG_FILE = "received.log"
ALERT_FILE = "alerts.txt"

SUSPICIOUS_PROCS = {"cmd.exe", "net.exe", "net1.exe"}
RENAME_TRACK = {}  # track rapid renames


LOG_RE = re.compile(
    r"^(?P<ts>[\d\-: ]+),\('\d+\.\d+\.\d+\.\d+', \d+\),\[(?P<state>[^\]]+)\]\s+(?P<data>.+)$"
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


def analyze_log(ts, state, data):
    now = datetime.now().isoformat()

    # ---- Process execution ----
    if state == "OPENED" and data.lower().endswith(".exe"):
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

    # ---- Process closed ----
    if state == "CLOSED" and data.lower() in SUSPICIOUS_PROCS:
        write_alert(
            ts, "process", data,
            "Medium", "Closed",
            "Log activity"
        )

    # ---- File created ----
    if state == "FILE CREATED":
        if "$Recycle.Bin" in data:
            write_alert(
                ts, "filesystem", data,
                "Medium", "Suspicious Location",
                "Monitor"
            )

    # ---- File renamed ----
    if state == "FILE RENAMED":
        old, new = data.split(" -> ")
        base = old.split("\\")[-1]

        RENAME_TRACK.setdefault(base, []).append(time.time())

        # rapid rename detection
        if len(RENAME_TRACK[base]) >= 2:
            write_alert(
                ts, old, new,
                "High", "Multiple Renames",
                "Quarantine File"
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
            state = m.group("state")
            data = m.group("data")

            analyze_log(ts, state, data)


if __name__ == "__main__":
    print("[+] Mini SOAR started. Monitoring received.log...")
    tail_log()

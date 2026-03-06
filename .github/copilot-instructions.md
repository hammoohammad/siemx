# SiemX AI Coding Instructions

## Architecture Overview
SiemX is a SIEM (Security Information and Event Management) system with separate backend and frontend components.

**Backend Components** (`SiemX Backend 2025/siemx/`):
- `monitor.py`: System monitoring agent using psutil/watchdog; sends events via socket to port 5051
- `edr.py`: Socket server (port 5051) receiving monitor data; logs to `received.log`
- `soar.py`: Security orchestration; analyzes `received.log` for threats; generates JSON alerts to `alerts.txt`
- `server.py`: FastAPI server (port 5000) with REST API and WebSocket; tails log files; serves normalized data to frontend
- `dashboard.py`: Tkinter GUI displaying real-time logs from socket connection

**Frontend Components** (`SIEMX Frontend 2025/SIEMX Frontend/`):
- React/Vite dashboard with Tailwind CSS; fetches data from backend API/WebSocket
- Screens: Dashboard, Alerts, Logs, Settings, AI Actions
- Real-time updates via WebSocket polling fallback

**Data Flow**:
1. Monitor → Socket (5051) → EDR → `received.log`
2. SOAR analyzes `received.log` → `alerts.txt`
3. Server tails both files → In-memory lists + MySQL DB → API/WebSocket → Frontend

## Key Patterns & Conventions

### Log Parsing & Normalization
Use flexible field mapping in normalizers (e.g., `timestamp`|`time`|`ts`):
```python
def normalize_alert(a: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": a.get("id") or a.get("_id") or f"a-{len(ALERTS)+1}-{int(datetime.utcnow().timestamp())}",
        "timestamp": a.get("timestamp") or a.get("time") or a.get("ts") or datetime.utcnow().isoformat() + "Z",
        # ... similar for source, destination, level, status, action
    }
```
Apply to all data structures for resilient parsing.

### File Paths & Locations
- Use relative paths from script directory: `BASE_DIR = os.path.dirname(__file__)`
- Log files: `received.log`, `alerts.txt` in backend root
- Monitor filesystem: `C:/` (Windows-specific)
- Avoid AppData paths in file monitoring

### Socket Communication
- Monitor sends formatted strings: `[OPENED] process.exe`, `[FILE CREATED] path`
- EDR receives on port 5051, logs with timestamp + client addr
- Admin code "5D4EE" enables privileged connection

### Alert Generation
JSON format in `alerts.txt`:
```json
{"timestamp": "2023-...", "source": "process", "destination": "cmd.exe", "level": "High", "status": "Detected", "action": "Monitor / Investigate"}
```
Trigger on suspicious processes (`cmd.exe`, `net.exe`), rapid file renames, etc.

### API Endpoints
- `/api/alerts`, `/api/logs`, `/api/insights` (GET)
- WebSocket `/ws` for real-time updates
- CORS allows `http://localhost:3000`

### Frontend Data Handling
- `useLiveData` hook: WebSocket primary, HTTP polling fallback (4s interval)
- Normalize incoming data client-side matching backend patterns
- Mock data in `src/data/mock.js` for development

## Development Workflows

### Starting the System
Run all backend scripts simultaneously:
```bash
cd SiemX\ Backend\ 2025/siemx/
start python edr.py && start python monitor.py && start python server.py && start python dashboard.py && start python soar.py
```
- EDR first (socket server), then monitor, server, etc.
- Frontend: `cd SIEMX\ Frontend\ 2025/SIEMX\ Frontend/ && npm run dev`

### Adding New Monitors
1. Extend `monitor.py` with new monitoring functions
2. Send formatted messages to socket: `sock.sendall(b"[EVENT] data\n")`
3. Update `soar.py` analysis logic for new event types
4. Add normalization in `server.py` if needed

### Modifying Alerts
- Edit `SUSPICIOUS_PROCS` in `soar.py`
- Add new analysis functions following `analyze_log()` pattern
- Ensure JSON output matches expected fields

### Database Integration
- MySQL table `logsnew1` with columns: timestamp, ip, port, state, info, severity
- Insert in `LogDB.insert_log()` after parsing
- In-memory lists in `server.py` for fast API access

## Dependencies & Environment
- Backend: `psutil`, `pywin32`, `watchdog`, `fastapi`, `uvicorn`, `mysql-connector-python`
- Frontend: Standard React/Vite with `recharts`, `lucide-react`, `date-fns`
- Windows-specific (psutil, win32gui); adapt for cross-platform
- MySQL database `siemx` required for log persistence

## Common Pitfalls
- Ensure socket ports (5051, 5000) are free
- Monitor requires admin privileges for full system access
- File tailing assumes UTF-8 encoding with error ignore
- Tkinter dashboard connects as "admin" with code "5D4EE"
import psutil
import win32gui
import win32process
import time
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

def get_active_window_process():
    """Get the process name of the current active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()  # handle of current window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name(), pid
    except Exception:
        return None, None

def monitor_programs():
    print("🔍 Monitoring opened and closed programs... (Press Ctrl+C to stop)\n")
    oldprograms = []
    open_programs = set()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    oldactivepid = 0
    try:
        while True:
            current_programs = set()
            newprogram = []
            # Scan all running processes
            for proc in psutil.process_iter(['pid', 'name']):
                current_programs.add(proc.info['name'])
                newprogram.append([proc.info['pid'],proc.info['name']])
                
            # Detect newly opened programs
            for n in newprogram:
                if n in oldprograms:
                    pass
                else:
                    print(f'{n} is opened')
                    msgo = f"[OPENED] {n[1]}"
                    sock.sendall(msgo.encode() + b"\n")
            for o in oldprograms:
                if o in newprogram:
                    pass
                else:
                    print(f'{o} is closed')
                    msgc = f"[CLOSED] {o[1]}"
                    sock.sendall(msgc.encode() + b"\n")
            oldprograms = newprogram
            # Detect current active window
            name, pid = get_active_window_process()
            if name:
                if pid != oldactivepid:
                    msg = f"[ACTIVE] {name}"
                    sock.sendall(msg.encode() + b"\n")
                    oldactivepid = pid

            time.sleep(2)  # check every 2 seconds

    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped.")

if __name__ == "__main__":
    monitor_programs()

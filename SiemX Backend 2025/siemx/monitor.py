import psutil
import win32gui
import win32process
import subprocess
import time
import socket
import pythoncom
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5051

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))

def get_active_window_process():
    """Get the process name of the current active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()  # handle of current window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name(), pid
    except Exception:
        return None, None
def monitor_users_and_groups():
    global sock
    print("[*] Starting User/Group monitor...")

    old_users = set()
    old_groups = set()

    while True:
        # Read user list
        users = set(subprocess.check_output("net user", shell=True, text=True).split())

        # Read group list
        groups = set(subprocess.check_output("net localgroup", shell=True, text=True).split())

        # Detect new users
        for u in users - old_users:
            print(f"[USER CREATED] {u}")
            sock.sendall(f"[USER CREATED] {u}\n".encode())

        # Detect deleted users
        for u in old_users - users:
            print(f"[USER DELETED] {u}")
            sock.sendall(f"[USER DELETED] {u}\n".encode())

        # Detect new groups
        for g in groups - old_groups:
            print(f"[GROUP CREATED] {g}")
            sock.sendall(f"[GROUP CREATED] {g}\n".encode())

        # Detect removed groups
        for g in old_groups - groups:
            print(f"[GROUP DELETED] {g}")
            sock.sendall(f"[GROUP DELETED] {g}\n".encode())

        old_users = users
        old_groups = groups

        time.sleep(2)   # Check every 2 seconds


# ================================
# FILE & DIRECTORY MONITORING
# ================================

class FSMonitor(FileSystemEventHandler):
    global sock
    def on_created(self, event):
        if event.is_directory:
            print(f"[DIR CREATED]  {event.src_path}")
            sock.sendall(f"[DIR CREATED]  {event.src_path}\n".encode())
        else:
            print(f"[FILE CREATED] {event.src_path}")
            if "Users" in event.src_path and "AppData" in event.src_path:
                pass
            else:
                sock.sendall(f"[FILE CREATED] {event.src_path}\n".encode()) 

    def on_deleted(self, event):
        if event.is_directory:
            print(f"[DIR DELETED]  {event.src_path}")
            sock.sendall(f"[DIR DELETED]  {event.src_path}\n".encode())
        else:
            print(f"[FILE DELETED] {event.src_path}")
            if "Users" in event.src_path and "AppData" in event.src_path:
                pass
            else:
                sock.sendall(f"[FILE DELETED] {event.src_path}\n".encode())


def monitor_filesystem(path_to_watch):
    print(f"[*] Watching directory: {path_to_watch}")

    event_handler = FSMonitor()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    
def monitor_programs():
    global sock
    print("🔍 Monitoring opened and closed programs... (Press Ctrl+C to stop)\n")
    oldprograms = []
    open_programs = set()
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
    t1 = threading.Thread(target=monitor_users_and_groups, daemon=True)
    t1.start()

    watch_path = "C:"
    t2 = threading.Thread(target=monitor_filesystem, args=(watch_path,), daemon=True)
    t2.start()
    monitor_programs()

import psutil
import win32gui
import win32process

def getprocname(pid):
    try:
        proc = psutil.Process(pid)
        return proc.name()
    except psutil.NoSuchProcess:
        print(f"No process found with PID ")
    except psutil.AccessDenied:
        print(f"Access denied to process with PID")

current_programs = []
for proc in psutil.process_iter(['pid', 'name']):
    current_programs.append(proc.info['pid'])
name = ''

print(name)


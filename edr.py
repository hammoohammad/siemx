import socket
import threading
import datetime
import os
import sys

HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096
CODE = "5D4EE"
LOG_FILE = os.path.join(os.path.dirname(__file__), "received.log")

admin = False
adminCon = None

def log_message(msg: str):
    global admin
    global adminCon
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    line = f"{timestamp} {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    if admin == True:
        adminCon.sendall(line.encode())

def handle_client(conn: socket.socket, addr):
    global admin
    global adminCon
    try:
        print(f"Connected: {addr}")
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            try:
                text = data.decode("utf-8", errors="replace")
            except Exception:
                text = repr(data)
            print(f"Received from {addr}: {text}")
            log_message(f"{addr} {text}")
            if text == CODE:
                conn.sendall('Connected to EDR Server'.encode())
                print('Code matched. Admin connected.')
                adminCon = conn
                admin = True
    except Exception as e:
        print(f"Error with {addr}: {e}")
    finally:
        conn.close()
        print(f"Disconnected: {addr}")

def run_server(host=HOST, port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"TCP server listening on {host}:{port}")
        try:
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                t.start()
        except KeyboardInterrupt:
            print("Shutting down server.")
        except Exception as e:
            print(f"Server error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run_server()
# ...existing code...
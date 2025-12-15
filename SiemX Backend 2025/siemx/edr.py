import socket
import threading
import datetime
import os
import sys
import mysql.connector

HOST = "127.0.0.1"
PORT = 5051
BUFFER_SIZE = 4096
CODE = "5D4EE"
LOG_FILE = os.path.join(os.path.dirname(__file__), "received.log")

admin = False
adminCon = None

class LogDB:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="siemx"
        )
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()   # optional but safer for multi-thread

    def insert(self, message):
        try:
            with self.lock:   # thread-safe insert
                sql = "INSERT INTO logs (msg) VALUES (%s)"
                self.cursor.execute(sql, (message,))
                self.conn.commit()
        except Exception as e:
            print("DB insert error:", e)

    def close(self):
        self.cursor.close()
        self.conn.close()
db = LogDB()

def log_message(msg: str):
    global admin
    global adminCon
    global db
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{formatted_time},{msg}\n"
    db.insert(line)
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
            log_message(f"{addr},{text}")
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
    global db
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
            db.close()
            print("Shutting down server.")
        except Exception as e:
            print(f"Server error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run_server()
# ...existing code...
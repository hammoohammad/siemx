import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5000

class LogServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Server")
        self.root.geometry("600x400")

        # Text area with scroll
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10))
        self.text_area.pack(expand=True, fill="both")

        self.running = True

        # Start socket server in background
        threading.Thread(target=self.start_server, daemon=True).start()

    def start_server(self):
        """Start TCP server and receive logs"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(5)
            self.root.after(0, self.log, f"🔌 Server listening on {HOST}:{PORT}")
            while self.running:
                conn, addr = s.accept()
                self.root.after(0, self.log, f"✅ Client connected: {addr}")
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        """Receive logs from one client"""
        with conn:
            while self.running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = data.decode(errors="ignore").strip()
                    self.root.after(0, self.log, msg)
                except:
                    break

    def log(self, message):
        """Print to GUI"""
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def on_close(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LogServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

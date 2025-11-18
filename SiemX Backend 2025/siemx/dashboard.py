import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5051

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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        msgo = "5D4EE"
        sock.sendall(msgo.encode())
        while True:
            chunk = sock.recv(4096)
            data = chunk.decode(errors="ignore")
            self.root.after(0, self.log, data)

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

import tkinter as tk
from tkinter import messagebox
# import client.main as client
import socket
import struct
import json
import threading

HOST = '127.0.0.1'  
PORT = 60000  

def connect():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        data_dict = {
            "status": "success",
            "type": "MOVE",
            "selected_pos": "a2",
            "target_pos": "e4",
        }

        client_socket.sendall(json.dumps(data_dict).encode("utf-8"))

        data = client_socket.recv(1024).decode('utf-8')
        data_dict = json.loads(data)

        print(f"Received: {data_dict}")

        client_socket.close()
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Connection Error", str(e)))

def connect_thread():
    threading.Thread(target=connect, daemon=True).start()

# --- Tkinter UI ---
root = tk.Tk()
root.title("Tkinter Socket Client")
root.geometry("640x480")

label = tk.Label(root, text="Click button to connect", font=("Sarabun", 12))
label.pack(pady=20)

btn1 = tk.Button(root, text="Send & Receive", command=connect_thread, width=20)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Quit", command=root.destroy, width=20)
btn2.pack(pady=10)

root.mainloop()
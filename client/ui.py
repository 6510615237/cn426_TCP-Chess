import tkinter as tk
from tkinter import messagebox
from client_logic import ChessClient

PORT = 60000
client = None  # Global client instance

def on_server_message(message):
    print("Server:", message)
    # You can update UI here later

def connect():
    ip = ip_entry.get()
    name = name_entry.get()
    room = room_entry.get()

    if not ip or not name or not room:
        messagebox.showerror("Missing Info", "Please fill in all fields.")
        return

    global client
    client = ChessClient(ip, PORT, name, room, on_receive_callback=on_server_message)
    success = client.connect()
    if success:
        messagebox.showinfo("Connected", f"Connected to {ip} as {name} in room {room}")
    else:
        messagebox.showerror("Connection Failed", "Could not connect to server.")

def send_move():
    if not client:
        messagebox.showerror("Not Connected", "Please connect first.")
        return

    from_pos = from_entry.get().strip()
    to_pos = to_entry.get().strip()

    if len(from_pos) != 2 or len(to_pos) != 2:
        messagebox.showerror("Invalid Input", "Please enter valid positions like 'a2' and 'a4'.")
        return

    client.send_move(from_pos, to_pos)

# --- Tkinter UI ---
root = tk.Tk()
root.title("Chess Client")
root.geometry("400x400")

tk.Label(root, text="Server IP:").pack()
ip_entry = tk.Entry(root)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack()

tk.Label(root, text="Your Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Room Name:").pack()
room_entry = tk.Entry(root)
room_entry.pack()

tk.Button(root, text="Connect", command=connect).pack(pady=10)

tk.Label(root, text="From Position (e.g., a2):").pack()
from_entry = tk.Entry(root)
from_entry.pack()

tk.Label(root, text="To Position (e.g., a4):").pack()
to_entry = tk.Entry(root)
to_entry.pack()

tk.Button(root, text="Send Move", command=send_move).pack(pady=10)
tk.Button(root, text="Quit", command=root.destroy).pack(pady=10)

root.mainloop()

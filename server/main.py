import socket
import struct
import threading

from handler import handle_client

HOST = '127.0.0.1'
PORT = 60000

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.settimeout(1)

    print(f"[LISTENING] Server running on {HOST}:{PORT}")

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
                # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            except socket.timeout:
                continue 
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN] Server stopped by user")
        server_socket.close()

if __name__ == "__main__":
    start_server()

import socket
import threading
import ssl

from handler import handle_client

HOST = '0.0.0.0'
PORT = 60000

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.settimeout(1)

    print(f"[LISTENING] Server running on {HOST}:{PORT}")

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
                secure_conn = context.wrap_socket(conn, server_side=True)

                thread = threading.Thread(
                    target=handle_client, 
                    args=(secure_conn, addr), 
                    daemon=True
                )

                # thread = threading.Thread(
                #     target=handle_client, 
                #     args=(conn, addr), 
                #     daemon=True
                # )


                thread.start()
            except socket.timeout:
                continue 
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN] Server stopped by user")
        server_socket.close()

if __name__ == "__main__":
    start_server()


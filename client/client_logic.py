import socket
import json
import threading
import ssl

class ChessClient:
    def __init__(self, host, port, name, room, on_receive_callback=None):
        self.host = host
        self.port = port
        self.name = name
        self.room = room
        self.sock = None
        self.listener_thread = None
        self.on_receive_callback = on_receive_callback


        # Send JOIN message

    def connect(self):
        try:

            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  

            self.sock = context.wrap_socket(raw_sock)
            self.sock.connect((self.host, self.port))

            # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self.sock.connect((self.host, self.port))

            join_msg = {
                "type": "JOIN",
                "name": self.name,
                "room": self.room
            }
            self.send_json(join_msg)

            # Start listener thread
            self.listener_thread = threading.Thread(target=self.listen, daemon=True)
            self.listener_thread.start()
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def send_move(self, from_pos, to_pos, promotion_to=None):
        """ Sends a move, now with an optional promotion choice. """
        move_msg = {
            "type": "MOVE",
            "selected_pos": from_pos,
            "target_pos": to_pos
        }
        if promotion_to:
            move_msg["promotion_to"] = promotion_to
        
        self.send_json(move_msg)

    def send_json(self, data):
        try:
            self.sock.sendall(json.dumps(data).encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] Send failed: {e}")

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if data:
                    message = json.loads(data.decode("utf-8"))
                    print(f"[RECEIVED] {message}")
                    if self.on_receive_callback:
                        self.on_receive_callback(message)
                else:
                    break
            except Exception as e:
                print(f"[ERROR] Listen failed: {e}")
                break

    def close(self):
        if self.sock:
            self.sock.close()
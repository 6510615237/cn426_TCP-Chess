import json
from game import ChessGame

def handle_client(conn, addr):

    board = ChessGame()
    board.print_board()

    print(f"[NEW CONNECTION] {addr}")
    try:
        client_reply = {
            "status": "success", # "fail"
            "message": f"Hello, client {addr}!",
            "result": "Move Made." # f"Invalid Move"
        }
    
        # Receive response from client
        data = conn.recv(1024)
        if data:
            print(f"[FROM {addr}] {data.decode()}")
            data_dict = json.loads(data.decode())

            result = board.make_move(data_dict["selected_pos"], data_dict["target_pos"])

            # If make_move fails, edit reply
            if not result:
                client_reply["status"] = "fail"
                client_reply["result"] = f"Invalid Move"

            conn.sendall(json.dumps(client_reply).encode('utf-8'))

        else:
            print(f"[{addr}] No data received (client closed)")
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")

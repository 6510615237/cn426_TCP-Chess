import json
from game import ChessGame

# Global room tracking
rooms = {}  # { "RoomName": { "players": [conn1, conn2], "roles": {conn1: "white", conn2: "black"}, "names": {conn1: "name1", conn2: "name2"}, "board": ChessGame() } }
client_rooms = {}  # { conn: "RoomName" }

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"[{addr}] No data received (client closed)")
                break

            print(f"[FROM {addr}] {data.decode()}")
            data_dict = json.loads(data.decode())
            msg_type = data_dict.get("type")

            if msg_type == "JOIN":
                name = data_dict.get("name")
                room = data_dict.get("room")

                if room not in rooms:
                    rooms[room] = {
                        "players": [],
                        "roles": {},
                        "names": {}, # <-- NEW: Add names dictionary
                        "board": ChessGame()
                    }

                if len(rooms[room]["players"]) >= 2:
                    conn.sendall(json.dumps({
                        "status": "fail",
                        "message": "Room is full. Only 2 players allowed."
                    }).encode("utf-8"))
                    return

                # Assign role
                role = "white" if len(rooms[room]["players"]) == 0 else "black"
                rooms[room]["players"].append(conn)
                rooms[room]["roles"][conn] = role
                rooms[room]["names"][conn] = name # <-- NEW: Store player's name
                client_rooms[conn] = room

                print(f"[JOIN] {name} joined room '{room}' as {role}")
                conn.sendall(json.dumps({
                    "status": "joined",
                    "room": room,
                    "role": role,
                    "message": f"Welcome {name}, you are playing as {role}."
                }).encode("utf-8"))
                
            elif msg_type == "MOVE":
                room = client_rooms.get(conn)
                if not room: continue # Safety check

                role = rooms[room]["roles"].get(conn)
                board = rooms[room]["board"]

                # Track turn (add this to room dict if not already)
                if "turn" not in rooms[room]:
                    rooms[room]["turn"] = "white"

                if rooms[room]["turn"] != role:
                    conn.sendall(json.dumps({
                        "status": "fail",
                        "message": f"Not your turn. It's {rooms[room]['turn']}'s turn."
                    }).encode("utf-8"))
                    continue
                
                # --- NEW: Get mover and opponent names ---
                mover_name = rooms[room]["names"].get(conn, "Player")
                opponent_name = "Opponent"
                for peer in rooms[room]["players"]:
                    if peer != conn:
                        opponent_name = rooms[room]["names"].get(peer, "Opponent")
                # --- END NEW ---
                
                from_pos = data_dict.get("selected_pos")
                to_pos = data_dict.get("target_pos")
                
                if not board.is_piece_owned_by(from_pos, role):
                    conn.sendall(json.dumps({
                        "status": "fail",
                        "message": f"You cannot move opponent's piece at {from_pos}."
                    }).encode("utf-8"))
                    continue
                
                # --- MODIFIED: Handle promotion ---
                promotion_to = data_dict.get("promotion_to")
                
                result, captured_piece, promoted_to_char = board.make_move(from_pos, to_pos, role, promotion_to)
                
                game_over = False
                winner = None
                winner_name = None # <-- NEW

                if result:
                    rooms[room]["turn"] = "black" if role == "white" else "white"
                    
                    if captured_piece and captured_piece.lower() == 'k':
                        game_over = True
                        winner = role
                        winner_name = mover_name # <-- NEW: The mover is the winner
                        print(f"[GAME OVER] {winner_name} wins in room {room}!")

                reply = {
                    "status": "success" if result else "fail",
                    "message": "Move Made." if result else "Invalid Move",
                    "from": from_pos,
                    "to": to_pos,
                    "captured": captured_piece if result else None,
                    "game_over": game_over,
                    "winner": winner, # 'white' or 'black'
                    "promoted_to": promoted_to_char,
                    "mover_name": mover_name, # <-- NEW
                    "opponent_name": opponent_name, # <-- NEW
                    "winner_name": winner_name # <-- NEW
                }
                # --- END MODIFICATION ---

                conn.sendall(json.dumps(reply).encode("utf-8"))

                # Broadcast to opponent
                for peer in rooms[room]["players"]:
                    if peer != conn:
                        peer.sendall(json.dumps({
                            "type": "UPDATE",
                            "from": from_pos,
                            "to": to_pos,
                            "status": reply["status"],
                            "captured": captured_piece if result else None,
                            "game_over": game_over,
                            "winner": winner,
                            "promoted_to": promoted_to_char,
                            "mover_name": mover_name, # <-- NEW
                            "opponent_name": opponent_name, # <-- NEW
                            "winner_name": winner_name # <-- NEW
                        }).encode("utf-8"))

            else:
                conn.sendall(json.dumps({
                    "status": "fail",
                    "message": "Unknown message type."
                }).encode("utf-8"))

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        # Clean up
        room = client_rooms.get(conn)
        if room and conn in rooms.get(room, {}).get("players", []):
            rooms[room]["players"].remove(conn)
            if conn in rooms[room]["roles"]:
                del rooms[room]["roles"][conn]
            print(f"[DISCONNECTED] {addr} left room '{room}'")
            if not rooms[room]["players"]:
                print(f"[CLEANUP] Deleting empty room '{room}'")
                del rooms[room]
        if conn in client_rooms:
            del client_rooms[conn]
        conn.close()
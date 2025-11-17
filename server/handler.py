import json
from game import ChessGame

# Global room tracking
rooms = {}  # { "RoomName": { "players": [conn1, conn2], "roles": {conn1: "white", conn2: "black"}, "board": ChessGame() } }
client_rooms = {}  # { conn: "RoomName" }

def broadcast_to_room(room, message_dict):
    """Send JSON message to all players in a room."""
    if room not in rooms:
        return
    for conn in rooms[room]["players"]:
        try:
            conn.sendall(json.dumps(message_dict).encode("utf-8"))
        except:
            pass

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
                        "board": ChessGame(),
                        "turn": "white"
                    }

                # Check if room is full
                if len(rooms[room]["players"]) >= 2:
                    conn.sendall(json.dumps({
                        "type": "JOIN_FAIL",
                        "message": "Room full (2 players max)"
                    }).encode("utf-8"))
                    continue

                # Add player to room
                role = "white" if len(rooms[room]["players"]) == 0 else "black"
                rooms[room]["players"].append(conn)
                rooms[room]["roles"][conn] = role
                client_rooms[conn] = room

                print(f"[JOIN] {name} joined '{room}' as {role}")

                # Send join success to this client  
                conn.sendall(json.dumps({
                    "type": "JOIN_OK",
                    "room": room,
                    "role": role,
                    "players": len(rooms[room]["players"])
                }).encode("utf-8"))

                # Send lobby update to **ALL** players in room
                broadcast_to_room(room, {
                    "type": "LOBBY_UPDATE",
                    "room": room,
                    "players": [
                        rooms[room]["roles"][p] 
                        for p in rooms[room]["players"]
                    ],
                    "total": len(rooms[room]["players"])
                })

                # Start game when 2 players are ready
                if len(rooms[room]["players"]) == 2:
                    broadcast_to_room(room, {
                        "type": "GAME_START",
                        "message": "Both players joined. Game starting..."
                    })
 
            elif msg_type == "MOVE":
                room = client_rooms.get(conn)
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
                
                from_pos = data_dict.get("selected_pos")
                to_pos = data_dict.get("target_pos")
                role = rooms[room]["roles"].get(conn)
                
                if not board.is_piece_owned_by(from_pos, role):
                    conn.sendall(json.dumps({
                        "status": "fail",
                        "message": f"You cannot move opponent's piece at {from_pos}."
                    }).encode("utf-8"))
                    continue
                
                result = board.make_move(from_pos, to_pos, role)

                if result:
                    rooms[room]["turn"] = "black" if role == "white" else "white"

                reply = {
                    "status": "success" if result else "fail",
                    "message": "Move Made." if result else "Invalid Move",
                    "from": from_pos,
                    "to": to_pos
                }

                conn.sendall(json.dumps(reply).encode("utf-8"))

                # Broadcast to opponent
                for peer in rooms[room]["players"]:
                    if peer != conn:
                        peer.sendall(json.dumps({
                            "type": "UPDATE",
                            "from": from_pos,
                            "to": to_pos,
                            "status": reply["status"]
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
            del rooms[room]["roles"][conn]
            print(f"[DISCONNECTED] {addr} left room '{room}'")
            if not rooms[room]["players"]:
                del rooms[room]
        if conn in client_rooms:
            del client_rooms[conn]
        conn.close()

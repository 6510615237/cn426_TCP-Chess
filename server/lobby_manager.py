from threading import Lock

class LobbyManager:
    def __init__(self):
        self.lobbies = {}
        self.lock = Lock()

    def join_lobby(self, room, name, conn):
        with self.lock:
            if room not in self.lobbies:
                self.lobbies[room] = {
                    "players": [],
                    "status": "waiting",
                    "game": None
                }
            
            lobby = self.lobbies[room]
            
            lobby["players"].append((name, conn))

            if len(lobby["players"]) == 2:
                lobby["status"] = "ready"

            return "OK"

    def get_status(self, room):
        with self.lock:
            if room not in self.lobbies:
                return None
            return self.lobbies[room]["status"]
        
    def get_players(self, room):
        with self.lock:
            if room not in self.lobbies:
                return []
            return [p[0] for p in self.lobbies[room]["players"]]
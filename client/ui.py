import tkinter as tk
from tkinter import messagebox, simpledialog, font
from client_logic import ChessClient
import threading
import json

# --- Configuration ---
HOST = '127.0.0.1' # <-- IMPORTANT: I changed this back to 127.0.0.1
PORT = 60000
BOARD_SIZE = 8
SQUARE_SIZE = 60
BOARD_DIM = BOARD_SIZE * SQUARE_SIZE
LIGHT_COLOR = "#EEEED2"
DARK_COLOR = "#769656"
SELECT_COLOR = "#BACA2B"
LEGAL_MOVE_EMPTY_COLOR = "#FFFF99" # A light-yellow dot
LEGAL_MOVE_CAPTURE_COLOR = "#FFD700" # A gold/yellow ring
PIECE_FONT_SIZE = 40

# --- Piece Mapping (from game.py to Unicode) ---
PIECE_UNICODE = {
    'R': '\u2656', 'N': '\u2658', 'B': '\u2657', 'Q': '\u2655', 'K': '\u2654', 'P': '\u2659',
    'r': '\u265C', 'n': '\u265E', 'b': '\u265D', 'q': '\u265B', 'k': '\u265A', 'p': '\u265F'
}

class ChessUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TCP Chess")
        self.geometry("500x650")
        self.resizable(False, False)

        self.client = None
        self.player_role = None  # 'white' or 'black'
        self.current_turn = 'white'
        self.selected_square = None
        self.legal_moves = [] # Holds list of (r, c) tuples for legal moves
        self.board_state = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

        self.piece_font = font.Font(family='Arial', size=PIECE_FONT_SIZE)

        # --- Connection Frame ---
        self.connection_frame = tk.Frame(self)
        self.connection_frame.pack(pady=20, fill="x", expand=True)
        
        tk.Label(self.connection_frame, text="Server IP:").pack()
        self.ip_entry = tk.Entry(self.connection_frame, width=20)
        self.ip_entry.insert(0, HOST)
        self.ip_entry.pack(pady=5)

        tk.Label(self.connection_frame, text="Your Name:").pack()
        self.name_entry = tk.Entry(self.connection_frame, width=20)
        self.name_entry.pack(pady=5)

        tk.Label(self.connection_frame, text="Room Name:").pack()
        self.room_entry = tk.Entry(self.connection_frame, width=20)
        self.room_entry.pack(pady=5)

        self.connect_button = tk.Button(self.connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=15)

        # --- Game Frame (Initially hidden) ---
        self.game_frame = tk.Frame(self)
        
        self.status_label = tk.Label(self.game_frame, text="Welcome! Connect to start.", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.turn_label = tk.Label(self.game_frame, text="Turn: White", font=("Arial", 12))
        self.turn_label.pack(pady=5)

        self.canvas = tk.Canvas(self.game_frame, width=BOARD_DIM, height=BOARD_DIM)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_board_click)
        
        self.draw_board()

    def connect_to_server(self):
        ip = self.ip_entry.get()
        name = self.name_entry.get()
        room = self.room_entry.get()

        if not ip or not name or not room:
            messagebox.showerror("Missing Info", "Please fill in all fields.")
            return

        try:
            # Pass the UI-thread-safe callback to the client
            self.client = ChessClient(ip, PORT, name, room, on_receive_callback=self.handle_server_message)
            if self.client.connect():
                messagebox.showinfo("Connected", f"Connected as {name} in room {room}")
                self.connection_frame.pack_forget()
                self.game_frame.pack(fill="both", expand=True)
            else:
                messagebox.showerror("Connection Failed", "Could not connect to server.")
                self.client = None
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.client = None

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = c * SQUARE_SIZE, r * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                
                # Determine square color
                color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
                
                # Highlight selected square
                if self.selected_square == (r, c):
                    color = SELECT_COLOR

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # --- NEW: Draw legal move indicators ---
                if (r, c) in self.legal_moves:
                    x_center = x1 + SQUARE_SIZE // 2
                    y_center = y1 + SQUARE_SIZE // 2
                    
                    if self.board_state[r][c] == ".":
                        # Draw a dot for empty squares
                        radius = SQUARE_SIZE // 6
                        self.canvas.create_oval(x_center - radius, y_center - radius,
                                                x_center + radius, y_center + radius,
                                                fill=LEGAL_MOVE_EMPTY_COLOR, outline="")
                    else:
                        # Draw a ring for captures
                        radius = SQUARE_SIZE // 2 - 3
                        self.canvas.create_oval(x_center - radius, y_center - radius,
                                                x_center + radius, y_center + radius,
                                                outline=LEGAL_MOVE_CAPTURE_COLOR, width=6)
                # --- END NEW ---

                # Draw piece
                piece_char = self.board_state[r][c]
                if piece_char != ".":
                    piece_unicode = PIECE_UNICODE.get(piece_char, "?")
                    # Center the piece in the square
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE // 2, 
                        y1 + SQUARE_SIZE // 2, 
                        text=piece_unicode, 
                        font=self.piece_font, 
                        fill="black" if piece_char.islower() else "white"
                    )
        
        # Add algebraic notation
        for i in range(BOARD_SIZE):
            # Files (a-h)
            self.canvas.create_text(
                i * SQUARE_SIZE + SQUARE_SIZE // 2,
                BOARD_DIM - 10,
                text=chr(ord('a') + i),
                font=("Arial", 10, "bold"),
                fill="#555555"
            )
            # Ranks (1-8)
            self.canvas.create_text(
                10,
                i * SQUARE_SIZE + SQUARE_SIZE // 2,
                text=str(BOARD_SIZE - i),
                font=("Arial", 10, "bold"),
                fill="#555555"
            )

    def on_board_click(self, event):
        if not self.client or not self.player_role:
            messagebox.showwarning("Wait", "Game has not started yet.")
            return
            
        if self.current_turn != self.player_role:
            self.update_status_label("Not your turn!", "red")
            return

        c = event.x // SQUARE_SIZE
        r = event.y // SQUARE_SIZE
        
        # Ensure click is within board bounds
        if c < 0 or c >= BOARD_SIZE or r < 0 or r >= BOARD_SIZE:
            return

        clicked_square_alg = self.index_to_algebraic(r, c)
        
        if self.selected_square is None:
            # --- First Click (Select Piece) ---
            piece = self.board_state[r][c]
            if piece == ".":
                return # Clicked on empty square
            
            # Check if player owns the piece
            if (self.player_role == 'white' and piece.islower()) or \
               (self.player_role == 'black' and piece.isupper()):
                self.update_status_label("You can't move opponent's piece.", "red")
                return
                
            self.selected_square = (r, c)
            self.legal_moves = self.get_legal_moves(r, c) # --- NEW: Get legal moves ---
            self.update_status_label(f"Selected {clicked_square_alg}")
            self.draw_board() # Redraw to show selection AND legal moves
        
        else:
            # --- Second Click (Select Target) ---
            src_r, src_c = self.selected_square
            src_alg = self.index_to_algebraic(src_r, src_c)
            dst_alg = clicked_square_alg
            
            self.legal_moves = [] # --- NEW: Clear legal moves ---

            # De-select if clicking the same square
            if (r, c) == self.selected_square:
                self.selected_square = None
                self.update_status_label("Selection cancelled.")
                self.draw_board()
                return

            # Send move to server
            print(f"[SENDING MOVE] From {src_alg} to {dst_alg}")
            self.client.send_move(src_alg, dst_alg)
            
            self.selected_square = None
            # Don't update the board here; wait for server confirmation.
            
    def handle_server_message(self, message):
        print(f"[UI RECEIVED] {message}")
        
        # Schedule the actual UI update on the main thread
        self.after(0, self.process_message_on_main_thread, message)

    def process_message_on_main_thread(self, message):
        """
        This method runs on the main UI thread and is safe to update Tkinter widgets.
        """
        try:
            status = message.get("status")
            msg_type = message.get("type")

            if status == "joined":
                self.player_role = message.get("role")
                self.title(f"TCP Chess - Playing as {self.player_role.capitalize()}")
                self.update_status_label(f"Joined as {self.player_role}. Waiting for opponent...", "blue")
                pass 
                
                self.draw_board()
            
            # --- MODIFIED: Handle new 'game_over' and 'captured' fields ---
            elif status == "success" or (msg_type == "UPDATE" and message.get("status") == "success"):
                
                from_pos = message.get("from")
                to_pos = message.get("to")
                captured_piece = message.get("captured")
                game_over = message.get("game_over")

                if from_pos and to_pos:
                    # Get info *before* making the move
                    from_r, from_c = self.algebraic_to_index(from_pos)
                    attacker_piece = self.board_state[from_r][from_c]
                    
                    # Make the move
                    self.perform_board_move(from_pos, to_pos)

                    if game_over:
                        winner = message.get("winner")
                        self.current_turn = '-' # Stop turns
                        self.update_turn_label()
                        self.update_status_label(f"GAME OVER! {winner.capitalize()} wins!", "blue")
                        self.canvas.unbind("<Button-1>") # Disable board
                        self.draw_board() # Final draw
                        messagebox.showinfo("Game Over", f"{winner.capitalize()} wins by capturing the King!")
                        return # Stop further processing

                    # --- Not game over, so update turn and status ---
                    self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                    self.update_turn_label()

                    # --- New Status Message Logic ---
                    if captured_piece and captured_piece != ".":
                        attacker_name = self.get_piece_name(attacker_piece)
                        captured_name = self.get_piece_name(captured_piece)
                        
                        if status == "success": # Your move
                            self.update_status_label(f"Your {attacker_name} captured {captured_name} on {to_pos}.")
                        else: # Opponent's move
                            self.update_status_label(f"Opponent's {attacker_name} captured {captured_name} on {to_pos}.")
                    else:
                        # Not a capture
                        if status == "success":
                            self.update_status_label(f"Move {from_pos} to {to_pos} successful.")
                        else: # Opponent's move
                            self.update_status_label(f"Opponent moved {from_pos} to {to_pos}.")
                    
                    self.draw_board() # Redraw after move
            # --- END MODIFICATION ---

            elif status == "fail":
                error_msg = message.get("message", "Invalid action")
                self.update_status_label(error_msg, "red")
                self.legal_moves = [] # Clear highlights on a failed move
                self.draw_board() # Redraw to remove selection highlight

        except Exception as e:
            print(f"[UI ERROR] Failed to process message: {e}")
            self.update_status_label(f"Error: {e}", "red")

    def perform_board_move(self, from_alg, to_alg):
        try:
            from_r, from_c = self.algebraic_to_index(from_alg)
            to_r, to_c = self.algebraic_to_index(to_alg)
            
            piece = self.board_state[from_r][from_c]
            self.board_state[to_r][to_c] = piece
            self.board_state[from_r][from_c] = "."
        except Exception as e:
            print(f"Error updating board state: {e}")

    def update_status_label(self, text, color="black"):
        self.status_label.config(text=text, fg=color)
        
    def update_turn_label(self):
        self.turn_label.config(text=f"Turn: {self.current_turn.capitalize()}")

    def index_to_algebraic(self, r, c):
        return f"{chr(ord('a') + c)}{BOARD_SIZE - r}"

    def algebraic_to_index(self, alg):
        try:
            c = ord(alg[0].lower()) - ord('a')
            r = BOARD_SIZE - int(alg[1])
            return r, c
        except Exception:
            return 0, 0 # Failsafe
        
    def on_closing(self):
        if self.client:
            self.client.close()
        self.destroy()

    # --- NEW: Helper function to get piece name ---
    def get_piece_name(self, piece_char):
        """Returns the full name of a piece character."""
        names = {'p': 'Pawn', 'r': 'Rook', 'n': 'Knight', 'b': 'Bishop', 'q': 'Queen', 'k': 'King'}
        return names.get(piece_char.lower(), 'Piece')
    # --- END NEW ---

    # --- Legal Move Logic (copied from server/game.py) ---
    
    def get_legal_moves(self, src_row, src_col):
        legal_moves = []
        if not self.player_role:
            return []
            
        src_alg = self.index_to_algebraic(src_row, src_col)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if r == src_row and c == src_col:
                    continue
                
                dst_alg = self.index_to_algebraic(r, c)
                if self.validate_move(src_alg, dst_alg, self.player_role):
                    legal_moves.append((r, c))
        return legal_moves

    def validate_move(self, src, dst, role):
        try:
            src_row, src_col = self.algebraic_to_index(src)
            dst_row, dst_col = self.algebraic_to_index(dst)
        except Exception:
            return False # Invalid algebraic notation

        piece = self.board_state[src_row][src_col]
        if piece == ".":
            return False

        # Ownership check
        if role == "white" and not piece.isupper():
            return False
        if role == "black" and not piece.islower():
            return False
        
        # Prevent capturing own piece
        dst_piece = self.board_state[dst_row][dst_col]
        if dst_piece != ".":
            if role == "white" and dst_piece.isupper():
                return False
            if role == "black" and dst_piece.islower():
                return False
            
        # Movement logic
        dr = dst_row - src_row
        dc = dst_col - src_col

        piece_type = piece.lower()

        if piece_type == "p":  # Pawn
            direction = -1 if role == "white" else 1
            start_row = 6 if role == "white" else 1

            # Move forward
            if dc == 0:
                if dr == direction and self.board_state[dst_row][dst_col] == ".":
                    return True
                # Check for 2-step move
                if src_row == start_row and dr == 2 * direction and \
                   self.board_state[dst_row][dst_col] == "." and \
                   self.board_state[src_row + direction][dst_col] == ".": # Check path is clear
                    return True

            # Capture
            if abs(dc) == 1 and dr == direction and self.board_state[dst_row][dst_col] != ".":
                return True

        elif piece_type == "r":  # Rook
            if dr == 0 or dc == 0:
                return self.is_path_clear(src_row, src_col, dst_row, dst_col)

        elif piece_type == "n":  # Knight
            return (abs(dr), abs(dc)) in [(2, 1), (1, 2)]

        elif piece_type == "b":  # Bishop
            if abs(dr) == abs(dc):
                return self.is_path_clear(src_row, src_col, dst_row, dst_col)

        elif piece_type == "q":  # Queen
            if dr == 0 or dc == 0 or abs(dr) == abs(dc):
                return self.is_path_clear(src_row, src_col, dst_row, dst_col)

        elif piece_type == "k":  # King
            return abs(dr) <= 1 and abs(dc) <= 1

        return False

    def is_path_clear(self, src_row, src_col, dst_row, dst_col):
        dr = dst_row - src_row
        dc = dst_col - src_col
        steps = max(abs(dr), abs(dc))
        step_r = dr // steps if steps != 0 else 0
        step_c = dc // steps if steps != 0 else 0

        for i in range(1, steps):
            r = src_row + i * step_r
            c = src_col + i * step_c
            if self.board_state[r][c] != ".":
                return False
        return True


if __name__ == "__main__":
    app = ChessUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
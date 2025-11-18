## Basic Chess Game

def algebraic_to_index(square):
        col = ord(square[0].lower()) - ord('a')
        row = 8 - int(square[1])
        return row, col

class ChessGame:

    def __init__(self):
        self.board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]
        self.PIECE_NAMES = {'q': 'Queen', 'r': 'Rook', 'b': 'Bishop', 'n': 'Knight'}


    def get_board(self):
        return self.board
    
    def print_board(self):
        for row in self.board:
            print(" ".join(row))
        print()

    def make_move(self, src, dst, role, promotion_to=None):
        """
        Attempts to make a move.
        Returns: (bool: success, str: captured_piece, str: promoted_char)
        """
        if not self.validate_move(src, dst, role):
            print(f"Invalid move for {role}: {src} to {dst}")
            return (False, None, None) # (Success, Captured, Promoted)
    
        src_row, src_col = algebraic_to_index(src)
        dst_row, dst_col = algebraic_to_index(dst)
    
        piece = self.board[src_row][src_col]
        captured_piece = self.board[dst_row][dst_col] # Get piece at destination
        
        self.board[dst_row][dst_col] = piece
        self.board[src_row][src_col] = "."
    
        print(f"{role} moved {piece} from {src} to {dst}")
        
        # --- Handle Promotion Logic ---
        promoted_char = None
        is_pawn = piece.lower() == 'p'
        is_last_rank = (role == 'white' and dst_row == 0) or (role == 'black' and dst_row == 7)
        
        if is_pawn and is_last_rank:
            if promotion_to and promotion_to.lower() in self.PIECE_NAMES:
                promoted_char = promotion_to.upper() if role == 'white' else promotion_to.lower()
                self.board[dst_row][dst_col] = promoted_char
                print(f"Pawn promoted to {promoted_char}!")
            else:
                # This is a server-side fallback, but client should always ask.
                promoted_char = 'Q' if role == 'white' else 'q'
                self.board[dst_row][dst_col] = promoted_char
                print(f"Pawn promoted to {promoted_char} (default)!")
        # --- END Promotion ---

        self.print_board()
        return (True, captured_piece, promoted_char) # Return success, captured, and promoted
    
    
    def is_piece_owned_by(self, square, role):
        row, col = algebraic_to_index(square)
        piece = self.board[row][col]
        if piece == ".":
            return False
        if role == "white":
            return piece.isupper()
        else:
            return piece.islower()
        
    def validate_move(self, src, dst, role, skip_self_check=False):
        try:
            src_row, src_col = algebraic_to_index(src)
            dst_row, dst_col = algebraic_to_index(dst)
        except Exception:
            return False

        piece = self.board[src_row][src_col]
        if piece == ".":
            return False

        # Ownership check
        if role == "white" and not piece.isupper():
            return False
        if role == "black" and not piece.islower():
            return False

        # Prevent capturing own piece
        dst_piece = self.board[dst_row][dst_col]
        if dst_piece != ".":
            if role == "white" and dst_piece.isupper():
                return False
            if role == "black" and dst_piece.islower():
                return False

        # Movement logic (pseudo-legal)
        dr = dst_row - src_row
        dc = dst_col - src_col
        piece_type = piece.lower()

        move_is_legal = False

        if piece_type == "p":  # Pawn
            direction = -1 if role == "white" else 1
            start_row = 6 if role == "white" else 1

            # 1-square forward
            if dc == 0 and dr == direction and self.board[dst_row][dst_col] == ".":
                move_is_legal = True

            # 2-square forward
            if (dc == 0 and src_row == start_row and dr == 2 * direction and
                self.board[dst_row][dst_col] == "." and
                self.board[src_row + direction][dst_col] == "."):
                move_is_legal = True

            # Capture
            if abs(dc) == 1 and dr == direction and self.board[dst_row][dst_col] != ".":
                move_is_legal = True

        elif piece_type == "r":  # Rook
            if dr == 0 or dc == 0:
                if self.is_path_clear(src_row, src_col, dst_row, dst_col):
                    move_is_legal = True

        elif piece_type == "n":  # Knight
            if (abs(dr), abs(dc)) in [(2, 1), (1, 2)]:
                move_is_legal = True

        elif piece_type == "b":  # Bishop
            if abs(dr) == abs(dc) and self.is_path_clear(src_row, src_col, dst_row, dst_col):
                move_is_legal = True

        elif piece_type == "q":  # Queen
            if (dr == 0 or dc == 0 or abs(dr) == abs(dc)) and \
            self.is_path_clear(src_row, src_col, dst_row, dst_col):
                move_is_legal = True

        elif piece_type == "k":  # King
            if abs(dr) <= 1 and abs(dc) <= 1:
                move_is_legal = True

        # If movement was illegal, no need to check king safety
        if not move_is_legal:
            return False

        # --- KING SAFETY CHECK ---
        if not skip_self_check:
            # Simulate the move
            saved_src = piece
            saved_dst = self.board[dst_row][dst_col]

            self.board[dst_row][dst_col] = piece
            self.board[src_row][src_col] = "."

            in_check = self.is_in_check(role)

            # Undo the move
            self.board[src_row][src_col] = saved_src
            self.board[dst_row][dst_col] = saved_dst

            if in_check:
                return False
        # --- END KING SAFETY CHECK ---

        return True
    
    def is_checkmate(self, role):
        if not self.is_in_check(role):
            return False  # must be in check

        # Try every legal move for this side
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == ".":
                    continue

                if role == "white" and not piece.isupper():
                    continue
                if role == "black" and not piece.islower():
                    continue

                # Try all 64 squares as target
                for rr in range(8):
                    for cc in range(8):
                        src = chr(c + ord('a')) + str(8 - r)
                        dst = chr(cc + ord('a')) + str(8 - rr)

                        # If the move is valid
                        if self.validate_move(src, dst, role):
                            # Simulate move
                            temp = self.board[rr][cc]
                            self.board[rr][cc] = piece
                            self.board[r][c] = "."

                            still_in_check = self.is_in_check(role)

                            # revert
                            self.board[r][c] = piece
                            self.board[rr][cc] = temp

                            if not still_in_check:
                                return False  # There is at least one escape move

        return True  # No escape → checkmate


    def is_path_clear(self, src_row, src_col, dst_row, dst_col):
        dr = dst_row - src_row
        dc = dst_col - src_col
        steps = max(abs(dr), abs(dc))
        step_r = dr // steps if steps != 0 else 0
        step_c = dc // steps if steps != 0 else 0

        for i in range(1, steps):
            r = src_row + i * step_r
            c = src_col + i * step_c
            if self.board[r][c] != ".":
                return False
        return True
    
    def find_king(self, role):
        king_char = "K" if role == "white" else "k"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king_char:
                    return r, c
        return None
    
    def is_square_attacked(self, row, col, by_role):
        # Try every piece of by_role, see if it can move to king square
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == ".":
                    continue

                if by_role == "white" and not piece.isupper():
                    continue
                if by_role == "black" and not piece.islower():
                    continue

                src = chr(c + ord('a')) + str(8 - r)
                dst = chr(col + ord('a')) + str(8 - row)

                if self.validate_move(src, dst, by_role, skip_self_check=True):
                    return True
        return False
    
    def is_in_check(self, role):
        king_row, king_col = self.find_king(role)
        opponent = "white" if role == "black" else "black"
        return self.is_square_attacked(king_row, king_col, opponent)



    def __str__(self):
        return self.print_board(self.board)
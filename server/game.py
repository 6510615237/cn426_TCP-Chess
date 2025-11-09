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

    def get_board(self):
        return self.board
    
    def print_board(self):
        for row in self.board:
            print(" ".join(row))
        print()

    def make_move(self, src, dst, role):
        if not self.validate_move(src, dst, role):
            print(f"Invalid move for {role}: {src} to {dst}")
            return False
    
        src_row, src_col = algebraic_to_index(src)
        dst_row, dst_col = algebraic_to_index(dst)
    
        piece = self.board[src_row][src_col]
        self.board[dst_row][dst_col] = piece
        self.board[src_row][src_col] = "."
    
        print(f"{role} moved {piece} from {src} to {dst}")
        self.print_board()
        return True
    
    
    def is_piece_owned_by(self, square, role):
        row, col = algebraic_to_index(square)
        piece = self.board[row][col]
        if piece == ".":
            return False
        if role == "white":
            return piece.isupper()
        else:
            return piece.islower()

    def validate_move(self, src, dst, role):
        src_row, src_col = algebraic_to_index(src)
        dst_row, dst_col = algebraic_to_index(dst)

        piece = self.board[src_row][src_col]
        if piece == ".":
            return False

        # Ownership check
        if role == "white" and not piece.isupper():
            return False
        if role == "black" and not piece.islower():
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
                if dr == direction and self.board[dst_row][dst_col] == ".":
                    return True
                if src_row == start_row and dr == 2 * direction and self.board[dst_row][dst_col] == ".":
                    return True

            # Capture
            if abs(dc) == 1 and dr == direction and self.board[dst_row][dst_col] != ".":
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
            if self.board[r][c] != ".":
                return False
        return True

    def __str__(self):
        return self.print_board(self.board)


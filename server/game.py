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

    def make_move(self, src, dst):
        try:
            print(src, dst)
            src_row, src_col = algebraic_to_index(src)
            dst_row, dst_col = algebraic_to_index(dst)

            piece = self.board[src_row][src_col]
            if piece == ".":
                print(f"No piece at {src}")
                return False

            # Move the piece
            self.board[dst_row][dst_col] = piece
            self.board[src_row][src_col] = "."

            print(f"Moved {piece} from {src} to {dst}")
            self.print_board()

            return True

        except Exception as e:
            print(f"Error: {e}")

            return False

    def __str__(self):
        return self.print_board(self.board)


import tkinter as tk
from tkinter import font
import math  # We'll use this for infinity


class NoughtsAndCrosses:
    def __init__(self, root):
        self.root = root
        self.root.title("Noughts and Crosses (Hard)")
        # Make the window non-resizable
        self.root.resizable(False, False)

        # Player and AI characters
        self.PLAYER_CHAR = 'X'
        self.AI_CHAR = 'O'

        # Game state
        self.board = [''] * 9
        self.game_active = True

        # --- Configure Fonts and Colors ---
        self.default_font = font.Font(family='Helvetica', size=16)
        self.board_font = font.Font(family='Helvetica', size=32, weight='bold')
        self.player_color = 'blue'
        self.ai_color = 'red'

        # --- Create Widgets ---

        # Status Label
        self.status_label = tk.Label(
            self.root,
            text="Your Turn (X)",
            font=self.default_font,
            pady=10
        )
        self.status_label.pack(fill=tk.X)

        # Frame for the 3x3 grid
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.buttons = []
        for i in range(9):
            button = tk.Button(
                self.board_frame,
                text='',
                font=self.board_font,
                width=4,
                height=2,
                relief='groove',
                command=lambda i=i: self.on_cell_click(i)
            )
            # Place button in the grid
            button.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(button)

        # Reset Button
        self.reset_button = tk.Button(
            self.root,
            text='New Game',
            font=self.default_font,
            command=self.reset_game
        )
        self.reset_button.pack(pady=10, fill=tk.X, padx=10)

    def on_cell_click(self, index):
        """Handles the human player's move."""

        # Check if the move is valid
        if self.board[index] == '' and self.game_active:

            # 1. Make the player's move
            self.update_cell(index, self.PLAYER_CHAR)

            # 2. Check if the player won
            # We pass self.board so the check_... functions can be reused by minimax
            if self.check_for_winner(self.PLAYER_CHAR, self.board):
                self.end_game(f"You win! ({self.PLAYER_CHAR})")
                return

            # 3. Check for a draw
            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

            # 4. It's the AI's turn
            self.status_label.config(text="Computer's Turn (O)")
            self.game_active = False  # Disable buttons during AI's turn
            # Call AI move after a short delay
            self.root.after(500, self.computer_move)

    def computer_move(self):
        """Handles the AI's move."""

        # Find the best possible move using the minimax algorithm
        move_index = self.find_best_move()

        if move_index is not None:
            self.update_cell(move_index, self.AI_CHAR)

            # 1. Check if the AI won
            if self.check_for_winner(self.AI_CHAR, self.board):
                self.end_game(f"Computer wins! ({self.AI_CHAR})")
                return

            # 2. Check for a draw
            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

        # 3. Return control to the player
        self.status_label.config(text="Your Turn (X)")
        self.game_active = True

    # --- AI LOGIC (MINIMAX) ---

    def find_best_move(self):
        """
        Main function to find the AI's best move.
        It iterates through all possible moves and calls minimax for each.
        """
        best_score = -math.inf
        best_move = None

        for i in range(9):
            if self.board[i] == '':
                # Try this move
                self.board[i] = self.AI_CHAR
                # Call minimax for the minimizing player (human)
                score = self.minimax(self.board, False)
                # Undo the move
                self.board[i] = ''

                # Update best score and move
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, current_board, is_maximizing):
        """
        The core minimax recursive algorithm.
        is_maximizing: True if it's the AI's turn, False for Player's turn.
        """

        # --- Check for terminal states (base cases) ---
        if self.check_for_winner(self.AI_CHAR, current_board):
            return 10  # AI wins
        if self.check_for_winner(self.PLAYER_CHAR, current_board):
            return -10  # Player wins
        if self.check_for_draw(current_board):
            return 0  # Draw

        # --- Recursive steps ---

        if is_maximizing:  # AI's turn (find MAX score)
            best_score = -math.inf
            for i in range(9):
                if current_board[i] == '':
                    current_board[i] = self.AI_CHAR
                    score = self.minimax(current_board, False)
                    current_board[i] = ''  # Undo move
                    best_score = max(score, best_score)
            return best_score

        else:  # Player's turn (find MIN score)
            best_score = math.inf
            for i in range(9):
                if current_board[i] == '':
                    current_board[i] = self.PLAYER_CHAR
                    score = self.minimax(current_board, True)
                    current_board[i] = ''  # Undo move
                    best_score = min(score, best_score)
            return best_score

    # --- HELPER & GAME STATE FUNCTIONS ---

    def update_cell(self, index, char):
        """Updates the board state and the button's appearance."""
        self.board[index] = char
        self.buttons[index].config(
            text=char,
            state='disabled',
            disabledforeground=(self.player_color if char == self.PLAYER_CHAR else self.ai_color)
        )

    def check_for_winner(self, char, board_state):
        """
        Checks if the given character has won the game on the given board_state.
        (Modified to accept a board_state for minimax simulations)
        """
        winning_moves = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)  # Diagonals
        ]
        for a, b, c in winning_moves:
            if board_state[a] == char and board_state[b] == char and board_state[c] == char:
                return True
        return False

    def check_for_draw(self, board_state):
        """
        Checks if the game is a draw on the given board_state.
        (Modified to accept a board_state for minimax simulations)
        """
        return '' not in board_state

    def end_game(self, message):
        """Disables the board and shows the result."""
        self.game_active = False
        self.status_label.config(text=message)
        for button in self.buttons:
            button.config(state='disabled')

    def reset_game(self):
        """Resets the game to its initial state."""
        self.board = [''] * 9
        self.game_active = True
        self.status_label.config(text="Your Turn (X)")
        for button in self.buttons:
            button.config(text='', state='normal')


# --- Main execution ---
if __name__ == "__main__":
    root = tk.Tk()
    game = NoughtsAndCrosses(root)
    # Start the Tkinter event loop
    root.mainloop()

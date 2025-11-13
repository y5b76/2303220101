import tkinter as tk
from tkinter import font
from tkinter import simpledialog  # Import the simple dialog box
import math
import random  # Import the random module


class NoughtsAndCrosses:
    def __init__(self, root):
        self.root = root
        self.root.title("Noughts and Crosses (Hard)")
        # Make the window non-resizable
        self.root.resizable(False, False)

        # --- Get Player and AI Names ---
        self.root.withdraw()  # Hide the main window temporarily

        # 1. Get Player Name
        self.player_name = simpledialog.askstring(
            "Player Name",
            "What is your name?",
            parent=self.root
        )
        # Set a default if the user cancels or enters nothing
        if not self.player_name:
            self.player_name = "Player"

        # 2. Get AI Name
        ai_names_list = ["Watson", "Arthur", "Merlin", "Hal", "Skynet", "Deep Blue"]
        self.ai_name = random.choice(ai_names_list)

        self.root.deiconify()  # Show the main window now
        # --- End Name Setup ---

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

        # Status Label - Now uses the player's name
        self.status_label = tk.Label(
            self.root,
            text=f"{self.player_name}'s Turn (X)",
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

        if self.board[index] == '' and self.game_active:

            self.update_cell(index, self.PLAYER_CHAR)

            if self.check_for_winner(self.PLAYER_CHAR, self.board):
                # Updated win message
                self.end_game(f"{self.player_name} wins! ({self.PLAYER_CHAR})")
                return

            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

            # Updated status message
            self.status_label.config(text=f"{self.ai_name}'s Turn (O)")
            self.game_active = False
            self.root.after(500, self.computer_move)

    def computer_move(self):
        """Handles the AI's move."""

        move_index = self.find_best_move()

        if move_index is not None:
            self.update_cell(move_index, self.AI_CHAR)

            if self.check_for_winner(self.AI_CHAR, self.board):
                # Updated win message
                self.end_game(f"{self.ai_name} wins! ({self.AI_CHAR})")
                return

            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

        # Updated status message
        self.status_label.config(text=f"{self.player_name}'s Turn (X)")
        self.game_active = True

    # --- AI LOGIC (MINIMAX - Unchanged) ---

    def find_best_move(self):
        best_score = -math.inf
        best_move = None

        for i in range(9):
            if self.board[i] == '':
                self.board[i] = self.AI_CHAR
                score = self.minimax(self.board, False)
                self.board[i] = ''

                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, current_board, is_maximizing):
        if self.check_for_winner(self.AI_CHAR, current_board):
            return 10
        if self.check_for_winner(self.PLAYER_CHAR, current_board):
            return -10
        if self.check_for_draw(current_board):
            return 0

        if is_maximizing:  # AI's turn
            best_score = -math.inf
            for i in range(9):
                if current_board[i] == '':
                    current_board[i] = self.AI_CHAR
                    score = self.minimax(current_board, False)
                    current_board[i] = ''
                    best_score = max(score, best_score)
            return best_score

        else:  # Player's turn
            best_score = math.inf
            for i in range(9):
                if current_board[i] == '':
                    current_board[i] = self.PLAYER_CHAR
                    score = self.minimax(current_board, True)
                    current_board[i] = ''
                    best_score = min(score, best_score)
            return best_score

    # --- HELPER & GAME STATE FUNCTIONS ---

    def update_cell(self, index, char):
        self.board[index] = char
        self.buttons[index].config(
            text=char,
            state='disabled',
            disabledforeground=(self.player_color if char == self.PLAYER_CHAR else self.ai_color)
        )

    def check_for_winner(self, char, board_state):
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
        return '' not in board_state

    def end_game(self, message):
        self.game_active = False
        self.status_label.config(text=message)
        for button in self.buttons:
            button.config(state='disabled')

    def reset_game(self):
        """Resets the game to its initial state."""
        self.board = [''] * 9
        self.game_active = True
        # Reset status label to use player's name
        self.status_label.config(text=f"{self.player_name}'s Turn (X)")
        for button in self.buttons:
            button.config(text='', state='normal')


# --- Main execution ---
if __name__ == "__main__":
    # Create the root window first
    root = tk.Tk()
    # Pass the root to the game class. The __init__ method will handle hiding/showing.
    game = NoughtsAndCrosses(root)
    # Start the Tkinter event loop
    root.mainloop()

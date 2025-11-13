import tkinter as tk
from tkinter import font
from tkinter import simpledialog, messagebox  # Added messagebox for the new option
import math
import random


class NoughtsAndCrosses:
    def __init__(self, root):
        self.root = root
        self.root.title("Noughts and Crosses")
        self.root.resizable(False, False)

        # --- Game Score ---
        self.player1_score = 0
        self.player2_score = 0
        self.WINNING_SCORE = 5

        # --- Player Characters ---
        self.PLAYER1_CHAR = 'X'
        self.PLAYER2_CHAR = 'O'

        # Start with Player 1
        self.current_player_char = self.PLAYER1_CHAR

        # --- Get Game Mode and Player Names ---
        self.root.withdraw()

        # Ask for game mode
        play_vs_human = messagebox.askyesno(
            "Game Mode",
            "Do you want to play against another human?"
        )

        if play_vs_human:
            self.game_mode = 'human'
            self.player1_name = simpledialog.askstring("Player 1", "What is Player 1's name (X)?", parent=self.root)
            self.player2_name = simpledialog.askstring("Player 2", "What is Player 2's name (O)?", parent=self.root)
            if not self.player1_name: self.player1_name = "Player 1"
            if not self.player2_name: self.player2_name = "Player 2"

        else:  # Play vs AI
            self.game_mode = 'cpu'
            self.player1_name = simpledialog.askstring("Player Name", "What is your name (X)?", parent=self.root)
            ai_names_list = ["Watson", "Arthur", "Merlin", "Hal", "Skynet", "Deep Blue"]
            self.player2_name = random.choice(ai_names_list)  # AI is Player 2
            if not self.player1_name: self.player1_name = "Player"

        self.root.deiconify()
        # --- End Setup ---

        # Game state
        self.board = [''] * 9
        self.game_active = True

        # --- Configure Fonts and Colors ---
        self.default_font = font.Font(family='Helvetica', size=16)
        self.board_font = font.Font(family='Helvetica', size=32, weight='bold')
        self.player1_color = 'blue'  # Player 1 (X)
        self.player2_color = 'red'  # Player 2 (O) or AI

        # --- Create Widgets ---

        # Score Label
        self.score_label = tk.Label(
            self.root,
            text=self.get_score_string(),
            font=self.default_font,
            pady=5
        )
        self.score_label.pack(fill=tk.X)

        # Status Label
        self.status_label = tk.Label(
            self.root,
            text=f"{self.player1_name}'s Turn (X)",
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
            button.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(button)

        # Reset/Next Round Button
        self.next_step_button = tk.Button(
            self.root,
            text='Next Round',
            font=self.default_font,
            command=self.handle_next_step_click,
            state='disabled'
        )
        self.next_step_button.pack(pady=10, fill=tk.X, padx=10)

    def on_cell_click(self, index):
        """Handles a click from either human player."""

        if self.board[index] == '' and self.game_active:

            # 1. Get current player info
            current_char = self.current_player_char
            current_name = self.player1_name if current_char == self.PLAYER1_CHAR else self.player2_name

            # 2. Make the move
            self.update_cell(index, current_char)

            # 3. Check for win
            if self.check_for_winner(current_char, self.board):
                self.end_game(f"{current_name} wins this round!", current_char)
                return

            # 4. Check for draw
            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

            # 5. Switch to the next player (or AI)
            if self.game_mode == 'human':
                if self.current_player_char == self.PLAYER1_CHAR:
                    self.current_player_char = self.PLAYER2_CHAR
                    self.status_label.config(text=f"{self.player2_name}'s Turn (O)")
                else:
                    self.current_player_char = self.PLAYER1_CHAR
                    self.status_label.config(text=f"{self.player1_name}'s Turn (X)")

            else:  # self.game_mode == 'cpu'
                # It's AI's turn
                self.status_label.config(text=f"{self.player2_name}'s Turn (O)")
                self.game_active = False
                self.root.after(500, self.computer_move)

    def computer_move(self):
        """Handles the AI's move (only called in 'cpu' mode)."""

        move_index = self.find_best_move()

        if move_index is not None:
            self.update_cell(move_index, self.PLAYER2_CHAR)

            if self.check_for_winner(self.PLAYER2_CHAR, self.board):
                self.end_game(f"{self.player2_name} wins this round!", self.PLAYER2_CHAR)
                return

            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

        # Return control to human player
        self.status_label.config(text=f"{self.player1_name}'s Turn (X)")
        self.game_active = True

    # --- AI LOGIC (MINIMAX) ---
    # This logic is now only used if self.game_mode == 'cpu'

    def find_best_move(self):
        best_score = -math.inf
        best_move = None

        for i in range(9):
            if self.board[i] == '':
                self.board[i] = self.PLAYER2_CHAR  # AI is Player 2
                score = self.minimax(self.board, False)
                self.board[i] = ''

                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, current_board, is_maximizing_ai):
        # AI (Player 2) is the maximizer
        if self.check_for_winner(self.PLAYER2_CHAR, current_board):
            return 10
        # Human (Player 1) is the minimizer
        if self.check_for_winner(self.PLAYER1_CHAR, current_board):
            return -10
        if self.check_for_draw(current_board):
            return 0

        if is_maximizing_ai:
            best_score = -math.inf
            for i in range(9):
                if current_board[i] == '':
                    current_board[i] = self.PLAYER2_CHAR
                    score = self.minimax(current_board, False)
                    current_board[i] = ''
                    best_score = max(score, best_score)
            return best_score

        else:  # Minimizing player's (Human's) turn
            best_score = math.inf
            for i in range(9):
                if current_board[i] == '':
                    current_board[i] = self.PLAYER1_CHAR
                    score = self.minimax(current_board, True)
                    current_board[i] = ''
                    best_score = min(score, best_score)
            return best_score

    # --- HELPER & GAME STATE FUNCTIONS ---

    def get_score_string(self):
        """Helper function to format the score."""
        return f"Score: {self.player1_name}: {self.player1_score}  -  {self.player2_name}: {self.player2_score}"

    def update_cell(self, index, char):
        self.board[index] = char
        color = self.player1_color if char == self.PLAYER1_CHAR else self.player2_color
        self.buttons[index].config(
            text=char,
            state='disabled',
            disabledforeground=color
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

    def end_game(self, message, winner_char=None):
        """Handles all end-of-round logic."""
        self.game_active = False
        self.status_label.config(text=message)
        for button in self.buttons:
            button.config(state='disabled')

        # Update Scores
        ultimate_winner_found = False
        if winner_char == self.PLAYER1_CHAR:
            self.player1_score += 1
        elif winner_char == self.PLAYER2_CHAR:
            self.player2_score += 1

        self.score_label.config(text=self.get_score_string())

        # Check for Ultimate Champion
        if self.player1_score == self.WINNING_SCORE:
            self.status_label.config(text=f"ULTIMATE CHAMPION: {self.player1_name}!!")
            self.next_step_button.config(text='Play Again? (Reset Score)')
            ultimate_winner_found = True
        elif self.player2_score == self.WINNING_SCORE:
            self.status_label.config(text=f"ULTIMATE CHAMPION: {self.player2_name}!!")
            self.next_step_button.config(text='Play Again? (Reset Score)')
            ultimate_winner_found = True

        if not ultimate_winner_found:
            self.next_step_button.config(text='Next Round')

        self.next_step_button.config(state='normal')

    def handle_next_step_click(self):
        """Decides whether to reset scores or just start a new round."""
        if self.player1_score == self.WINNING_SCORE or self.player2_score == self.WINNING_SCORE:
            self.full_game_reset()
        else:
            self.start_new_round()

    def start_new_round(self):
        """Resets the board for the next round (keeps scores)."""
        self.board = [''] * 9
        self.game_active = True
        # Always start with Player 1 (X)
        self.current_player_char = self.PLAYER1_CHAR
        self.status_label.config(text=f"{self.player1_name}'s Turn (X)")
        for button in self.buttons:
            button.config(text='', state='normal')
        self.next_step_button.config(state='disabled')

    def full_game_reset(self):
        """Resets the scores and the board."""
        self.player1_score = 0
        self.player2_score = 0
        self.score_label.config(text=self.get_score_string())
        self.next_step_button.config(text='Next Round')
        self.start_new_round()


# --- Main execution ---
if __name__ == "__main__":
    root = tk.Tk()
    game = NoughtsAndCrosses(root)
    root.mainloop()
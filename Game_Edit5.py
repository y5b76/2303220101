import tkinter as tk
from tkinter import font
from tkinter import simpledialog, messagebox
import math
import random

# --- Sound Import ---
try:
    import winsound

    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False
    print("Note: 'winsound' module not found. Disabling sound effects.")


# --- End Sound Import ---

class NoughtsAndCrosses:
    def __init__(self, root):
        self.root = root
        self.root.title("Noughts and Crosses")
        self.root.resizable(False, False)
        # --- 1. Set main window background ---
        self.root.config(bg='purple')

        # --- Game Score ---
        self.player1_score = 0
        self.player2_score = 0
        self.WINNING_SCORE = 5

        # --- Player Characters ---
        self.PLAYER1_CHAR = 'X'
        self.PLAYER2_CHAR = 'O'

        self.current_player_char = self.PLAYER1_CHAR

        # --- Get Game Mode and Player Names ---
        self.root.withdraw()

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
            self.player2_name = random.choice(ai_names_list)
            if not self.player1_name: self.player1_name = "Player"

        self.root.deiconify()
        # --- End Setup ---

        self.board = [''] * 9
        self.game_active = True

        # --- Configure Fonts and Colors ---
        self.default_font = font.Font(family='Helvetica', size=16)
        self.board_font = font.Font(family='Helvetica', size=32, weight='bold')
        # --- 2. Change X/O colors for better contrast on purple ---
        self.player1_color = 'cyan'
        self.player2_color = 'gold'

        # --- Create Widgets ---

        # --- 3. Set Label backgrounds ---
        self.score_label = tk.Label(
            self.root,
            text=self.get_score_string(),
            font=self.default_font,
            pady=5,
            bg='purple',
            fg='white'
        )
        self.score_label.pack(fill=tk.X)

        self.status_label = tk.Label(
            self.root,
            text=f"{self.player1_name}'s Turn (X)",
            font=self.default_font,
            pady=10,
            bg='purple',
            fg='white'
        )
        self.status_label.pack(fill=tk.X)

        # --- 4. Set Frame background ---
        self.board_frame = tk.Frame(self.root, bg='purple')
        self.board_frame.pack()

        self.buttons = []
        for i in range(9):
            # --- 5. Style the 9 grid buttons ---
            button = tk.Button(
                self.board_frame,
                text='',
                font=self.board_font,
                width=4,
                height=2,
                relief='groove',
                command=lambda i=i: self.on_cell_click(i),
                bg='#e0b0ff',  # Light purple
                activebackground='#c080ff'  # Darker light purple on click
            )
            button.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.buttons.append(button)

        # --- 6. Style the 'Next Round' button ---
        self.next_step_button = tk.Button(
            self.root,
            text='Next Round',
            font=self.default_font,
            command=self.handle_next_step_click,
            state='disabled',
            bg='#4a148c',  # A darker purple
            fg='white',
            activebackground='#6a1b9a',  # A lighter purple when clicked
            activeforeground='white'
        )
        self.next_step_button.pack(pady=10, fill=tk.X, padx=10)

    def on_cell_click(self, index):
        """Handles a click from either human player."""

        if self.board[index] == '' and self.game_active:

            current_char = self.current_player_char
            current_name = self.player1_name if current_char == self.PLAYER1_CHAR else self.player2_name

            self.update_cell(index, current_char)

            # --- 7. Highlight winning buttons ---
            winner_line = self.check_for_winner(current_char, self.board)
            if winner_line:
                self.highlight_winner(winner_line)
                self.end_game(f"{current_name} wins this round!", current_char)
                return

            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

            if self.game_mode == 'human':
                if self.current_player_char == self.PLAYER1_CHAR:
                    self.current_player_char = self.PLAYER2_CHAR
                    self.status_label.config(text=f"{self.player2_name}'s Turn (O)")
                else:
                    self.current_player_char = self.PLAYER1_CHAR
                    self.status_label.config(text=f"{self.player1_name}'s Turn (X)")

            else:  # self.game_mode == 'cpu'
                self.status_label.config(text=f"{self.player2_name}'s Turn (O)")
                self.game_active = False
                self.root.after(500, self.computer_move)

    def computer_move(self):
        """Handles the AI's move (only called in 'cpu' mode)."""

        move_index = self.find_best_move()

        if move_index is not None:
            self.update_cell(move_index, self.PLAYER2_CHAR)

            # --- 7. Highlight winning buttons ---
            winner_line = self.check_for_winner(self.PLAYER2_CHAR, self.board)
            if winner_line:
                self.highlight_winner(winner_line)
                self.end_game(f"{self.player2_name} wins this round!", self.PLAYER2_CHAR)
                return

            if self.check_for_draw(self.board):
                self.end_game("It's a draw!")
                return

        self.status_label.config(text=f"{self.player1_name}'s Turn (X)")
        self.game_active = True

    # --- AI LOGIC (MINIMAX - Unchanged) ---

    def find_best_move(self):
        best_score = -math.inf
        best_move = None
        for i in range(9):
            if self.board[i] == '':
                self.board[i] = self.PLAYER2_CHAR
                score = self.minimax(self.board, False)
                self.board[i] = ''
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move

    def minimax(self, current_board, is_maximizing_ai):
        if self.check_for_winner(self.PLAYER2_CHAR, current_board):
            return 10
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
        else:
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
        return f"Score: {self.player1_name}: {self.player1_score}  -  {self.player2_name}: {self.player2_score}"

    def update_cell(self, index, char):
        self.board[index] = char
        color = self.player1_color if char == self.PLAYER1_CHAR else self.player2_color
        self.buttons[index].config(
            text=char,
            state='disabled',
            disabledforeground=color,
            bg='#a080c0'  # Set a disabled background color
        )

        if SOUND_ENABLED:
            winsound.Beep(1200, 75)

    def check_for_winner(self, char, board_state):
        winning_moves = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)  # Diagonals
        ]
        for move in winning_moves:
            a, b, c = move
            if board_state[a] == char and board_state[b] == char and board_state[c] == char:
                return move  # Return the winning line
        return None  # Return None if no winner

    def highlight_winner(self, winning_line):
        """Changes the background of the winning buttons."""
        for index in winning_line:
            self.buttons[index].config(bg='gold')

    def check_for_draw(self, board_state):
        return '' not in board_state

    def end_game(self, message, winner_char=None):
        """Handles all end-of-round logic."""
        self.game_active = False
        self.status_label.config(text=message)
        # Disable all *other* buttons
        for i, button in enumerate(self.buttons):
            if button.cget('state') == 'normal':
                button.config(state='disabled', bg='#a080c0')

        if SOUND_ENABLED:
            if winner_char is not None:
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
            else:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)

        # ... (Score logic remains the same) ...
        ultimate_winner_found = False
        if winner_char == self.PLAYER1_CHAR:
            self.player1_score += 1
        elif winner_char == self.PLAYER2_CHAR:
            self.player2_score += 1

        self.score_label.config(text=self.get_score_string())

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
        self.current_player_char = self.PLAYER1_CHAR
        self.status_label.config(text=f"{self.player1_name}'s Turn (X)")
        for button in self.buttons:
            # --- 8. Reset button style ---
            button.config(
                text='',
                state='normal',
                bg='#e0b0ff'  # Reset to light purple
            )
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
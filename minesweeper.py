import tkinter as tk
import random
import csv
import os
import pickle
from tkinter import messagebox
from collections import deque
from datetime import datetime

levels = {
    'beginner': {'size_x': 8, 'size_y': 8, 'num_mines': 10, 'num_treasures': random.randint(1, 3)},
    'intermediate': {'size_x': 16, 'size_y': 16, 'num_mines': 40, 'num_treasures': random.randint(4, 8)},
    'expert': {'size_x': 30, 'size_y': 16, 'num_mines': 99, 'num_treasures': random.randint(9, 12)}
}

BTN_FLAG_EVENTS = ["<Button-2>", "<Button-3>", "<Control-Button-1>"]

class Cell:
    def __init__(self, x, y):
        """
        Requires:
            - x (int): The row index of the cell.
            - y (int): The column index of the cell.
        Ensures:
            - Initializes the cell with default properties.
        """
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_flagged = False
        self.is_revealed = False
        self.adjacent_mines = 0
        self.has_treasure = False
        self.rect_id = None
        self.text_id = None

class GameModel:
    def __init__(self, size_x, size_y, num_mines, num_treasures, level_name, test_board=None):
        """
        Requires:
            - size_x (int): Number of rows on the board.
            - size_y (int): Number of columns on the board.
            - num_mines (int): Total number of mines to place.
            - num_treasures (int): Total number of treasures to place.
            - level_name (str): Name of the game level.
            - test_board (list of lists, optional): Predefined board for testing mode.
        Ensures:
            - A board of size_x by size_y is initialized.
            - Mines and treasures are placed based on test_board or randomly.
            - adjacent_mines counts are calculated for each cell.
        """
        self.size_x = size_x
        self.size_y = size_y
        self.num_mines = num_mines
        self.num_treasures = num_treasures
        self.level_name = level_name
        self.board = [[Cell(x, y) for y in range(size_y)] for x in range(size_x)]
        self.mines = 0
        self.start_time = None
        self.flag_count = 0
        self.clicked_count = 0
        self.treasure_cells = []
        self.test_board = test_board
        self.is_test_mode = test_board is not None
        if test_board:
            self.initialize_board_from_test_board(test_board)
        else:
            self.place_mines()
            self.calculate_adjacent_mines()
            self.place_treasures()

    def initialize_board_from_test_board(self, test_board):
        """
        Requires:
            - test_board (list of lists): Predefined board configuration.
        Ensures:
            - Initializes the board with mines and treasures as per test_board.
            - Calculates adjacent mine counts.
        """
        for x in range(self.size_x):
            for y in range(self.size_y):
                value = test_board[x][y]
                if value == 1:
                    self.board[x][y].is_mine = True
                    self.mines += 1
                elif value == 2:
                    self.board[x][y].has_treasure = True
                    self.treasure_cells.append(self.board[x][y])
        self.num_treasures = len(self.treasure_cells)
        self.calculate_adjacent_mines()

    def place_mines(self):
        """
        Requires:
            - No mines have been placed yet.
        Ensures:
            - Randomly places num_mines mines on the board.
        """
        all_cells = [cell for row in self.board for cell in row]
        mine_cells = random.sample(all_cells, self.num_mines)
        for cell in mine_cells:
            cell.is_mine = True
            self.mines += 1

    def calculate_adjacent_mines(self):
        """
        Requires:
            - Mines have been placed on the board.
        Ensures:
            - Calculates and assigns the number of adjacent mines for each cell.
        """
        for row in self.board:
            for cell in row:
                cell.adjacent_mines = self.count_adjacent_mines(cell)

    def count_adjacent_mines(self, cell):
        """
        Requires:
            - cell is a valid Cell object on the board.
        Ensures:
            - Returns the count of mines adjacent to the given cell.
        """
        count = 0
        for neighbor in self.get_neighbors(cell.x, cell.y):
            if neighbor.is_mine:
                count += 1
        return count

    def get_neighbors(self, x, y):
        """
        Requires:
            - x and y are valid indices within the board.
        Ensures:
            - Returns a list of neighboring cells around the given (x, y) position.
        """
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx != 0 or dy != 0) and 0 <= nx < self.size_x and 0 <= ny < self.size_y:
                    neighbors.append(self.board[nx][ny])
        return neighbors

    def place_treasures(self):
        """
        Requires:
            - Mines have been placed on the board.
        Ensures:
            - Randomly places num_treasures treasures on non-mine cells.
        """
        available_cells = [cell for row in self.board for cell in row if not cell.is_mine]
        if len(available_cells) >= self.num_treasures:
            treasure_cells = random.sample(available_cells, self.num_treasures)
            for cell in treasure_cells:
                cell.has_treasure = True
                self.treasure_cells.append(cell)

    def is_adjacent_to_treasure(self, cell):
        """
        Requires:
            - cell is a valid Cell object on the board.
        Ensures:
            - Returns True if the cell is adjacent to any treasure, False otherwise.
        """
        for treasure in self.treasure_cells:
            treasure_neighbors = self.get_neighbors(treasure.x, treasure.y)
            if cell in treasure_neighbors:
                return True
        return False

class GameController:
    def __init__(self, model, view):
        """
        Requires:
            - model (GameModel): The game model instance.
            - view (GUIView or TextView): The game view instance.
        Ensures:
            - Initializes the controller with the given model and view.
        """
        self.model = model
        self.view = view

    def start_game(self):
        """
        Requires:
            - The game model and view are initialized.
        Ensures:
            - Starts the game by drawing the board.
        """
        self.view.draw_board()

    def on_click(self, x, y):
        """
        Requires:
            - x and y are valid cell coordinates.
            - The cell at (x, y) is not already revealed or flagged.
        Ensures:
            - Reveals the cell.
            - If the cell is a mine, triggers game over with a loss.
            - If the cell has a treasure, triggers game over with a win.
            - If the cell has zero adjacent mines, recursively reveals adjacent cells.
            - Updates the view accordingly.
            - Checks for a win condition.
        """
        cell = self.model.board[x][y]
        if self.model.start_time is None:
            self.model.start_time = datetime.now()
            self.view.start_time = self.model.start_time
        if cell.is_revealed or cell.is_flagged:
            return
        cell.is_revealed = True
        self.model.clicked_count += 1
        if cell.is_mine:
            if hasattr(self.view, 'update_cell'):
                self.view.update_cell(cell)
            self.view.game_over(False)
            return
        elif cell.has_treasure:
            if hasattr(self.view, 'update_cell'):
                self.view.update_cell(cell)
            self.view.game_over(True)
            return
        if cell.adjacent_mines == 0:
            self.reveal_empty_cells(cell)
        else:
            if hasattr(self.view, 'update_cell'):
                self.view.update_cell(cell)
        total_safe_cells = self.model.size_x * self.model.size_y - self.model.mines - self.model.num_treasures
        if self.model.clicked_count == total_safe_cells:
            self.view.game_over(True)

    def on_right_click(self, x, y):
        """
        Requires:
            - x and y are valid cell coordinates.
            - The cell at (x, y) is not already revealed.
        Ensures:
            - Toggles the flagged state of the cell.
            - Updates the flag count.
            - Updates the view accordingly.
        """
        cell = self.model.board[x][y]
        if cell.is_revealed:
            return
        if not cell.is_flagged:
            cell.is_flagged = True
            self.model.flag_count += 1
        else:
            cell.is_flagged = False
            self.model.flag_count -= 1
        if hasattr(self.view, 'update_cell'):
            self.view.update_cell(cell)
        if hasattr(self.view, 'refresh_labels'):
            self.view.refresh_labels()

    def reveal_empty_cells(self, cell):
        """
        Requires:
            - cell is a revealed cell with zero adjacent mines.
        Ensures:
            - Recursively reveals all adjacent non-mine, non-flagged cells.
            - Stops recursion at cells adjacent to treasures.
            - Updates the view accordingly.
        """
        queue = deque()
        queue.append(cell)
        while queue:
            current = queue.popleft()
            if hasattr(self.view, 'update_cell'):
                self.view.update_cell(current)
            for neighbor in self.model.get_neighbors(current.x, current.y):
                if (not neighbor.is_revealed and not neighbor.is_mine and not neighbor.is_flagged):
                    if neighbor.has_treasure:
                        continue
                    if self.model.is_adjacent_to_treasure(neighbor):
                        continue
                    neighbor.is_revealed = True
                    self.model.clicked_count += 1
                    if hasattr(self.view, 'update_cell'):
                        self.view.update_cell(neighbor)
                    if neighbor.adjacent_mines == 0:
                        queue.append(neighbor)
        total_safe_cells = self.model.size_x * self.model.size_y - self.model.mines - self.model.num_treasures
        if self.model.clicked_count == total_safe_cells:
            self.view.game_over(True)

    def restart_game(self):
        """
        Requires:
            - The game has ended.
        Ensures:
            - Reinitializes the game model with the same test_board if in testing mode.
            - Resets the view.
            - Starts a new game.
        """
        self.clear_saved_game()
        if self.model.test_board:
            self.model = GameModel(
                self.model.size_x,
                self.model.size_y,
                self.model.num_mines,
                self.model.num_treasures,
                level_name=self.model.level_name,
                test_board=self.model.test_board
            )
        else:
            self.model = GameModel(
                self.model.size_x,
                self.model.size_y,
                self.model.num_mines,
                self.model.num_treasures,
                level_name=self.model.level_name
            )
        self.view.model = self.model
        self.view.controller = self
        self.view.reset_view()
        self.start_game()

    def save_game(self):
        """
        Requires:
            - The game is in progress and not in testing mode.
        Ensures:
            - Saves the current game state to a file named after the level.
        """
        if not self.model.is_test_mode:
            with open(f"{self.model.level_name}.sav", "wb") as f:
                pickle.dump(self.model, f)

    def clear_saved_game(self):
        """
        Requires:
            - The game has ended.
        Ensures:
            - Removes the saved game file if it exists.
        """
        if not self.model.is_test_mode:
            saved_game_file = f"{self.model.level_name}.sav"
            if os.path.exists(saved_game_file):
                os.remove(saved_game_file)

class GUIView:
    def __init__(self, model, controller):
        """
        Requires:
            - model (GameModel): The game model instance.
            - controller (GameController): The game controller instance.
        Ensures:
            - Initializes the GUI components and binds event handlers.
        """
        self.model = model
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        self.root.focus_force()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.labels = {
            "time": tk.Label(self.frame, text="00:00:00"),
            "mines": tk.Label(self.frame, text=f"Mines: {self.model.mines}"),
            "flags": tk.Label(self.frame, text="Flags: 0"),
            "treasures": tk.Label(self.frame, text=f"Treasures: {self.model.num_treasures}")
        }
        self.labels["time"].pack()
        self.labels["mines"].pack(side='left')
        self.labels["flags"].pack(side='right')
        self.labels["treasures"].pack(side='top')
        self.start_time = self.model.start_time
        if self.model.size_x <= 8:
            self.CELL_SIZE = 50
        elif self.model.size_x <= 16:
            self.CELL_SIZE = 30
        else:
            self.CELL_SIZE = 20
        self.canvas = tk.Canvas(self.root, width=self.model.size_y * self.CELL_SIZE, height=self.model.size_x * self.CELL_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        for event in BTN_FLAG_EVENTS:
            self.canvas.bind(event, self.on_canvas_right_click)

        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Quit", command=self.on_quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)
        self.update_timer()

    def draw_board(self):
        """
        Requires:
            - model has been initialized with mines and treasures placed.
            - view components are properly set up.
        Ensures:
            - Draws the grid of cells on the canvas.
            - Initializes the visual representation of each cell.
            - Refreshes the labels to display current game information.
        """
        for x in range(self.model.size_x):
            for y in range(self.model.size_y):
                cell = self.model.board[x][y]
                x1 = y * self.CELL_SIZE
                y1 = x * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill='gray',
                    outline='black',
                    width=1
                )
                cell.rect_id = rect_id
                cell.text_id = self.canvas.create_text(
                    x1 + self.CELL_SIZE / 2,
                    y1 + self.CELL_SIZE / 2,
                    text='',
                    font=('Helvetica', max(8, int(self.CELL_SIZE / 2)))
                )
        for row in self.model.board:
            for cell in row:
                self.update_cell(cell)
        self.refresh_labels()

    def reset_view(self):
        """
        Requires:
            - A new game model has been initialized.
        Ensures:
            - Clears the canvas and resets all visual components.
            - Resets the labels to display the updated number of mines and treasures.
            - Draws the new game board.
        """
        self.canvas.delete("all")
        self.start_time = self.model.start_time
        self.labels["time"].config(text="00:00:00")
        self.labels["treasures"].config(text=f"Treasures: {self.model.num_treasures}")
        self.labels["mines"].config(text=f"Mines: {self.model.mines}")
        self.labels["flags"].config(text="Flags: 0")
        self.draw_board()

    def update_cell(self, cell):
        """
        Requires:
            - cell is a valid Cell object on the board.
            - cell's state has been updated (revealed or flagged).
        Ensures:
            - Updates the visual representation of the cell based on its state.
        """
        if cell.is_revealed:
            if cell.is_mine:
                self.canvas.itemconfig(cell.rect_id, fill='#FFCCCC')
                self.canvas.itemconfig(cell.text_id, text='M', fill='#CC0000')
            elif cell.has_treasure:
                self.canvas.itemconfig(cell.rect_id, fill='#CCFFCC')
                self.canvas.itemconfig(cell.text_id, text='T', fill='#006600')
            elif cell.adjacent_mines > 0:
                self.canvas.itemconfig(cell.rect_id, fill='white')
                self.canvas.itemconfig(cell.text_id, text=str(cell.adjacent_mines), fill='black')
            else:
                self.canvas.itemconfig(cell.rect_id, fill='white')
                self.canvas.itemconfig(cell.text_id, text='')
        elif cell.is_flagged:
            self.canvas.itemconfig(cell.rect_id, fill='#CCE5FF')
            self.canvas.itemconfig(cell.text_id, text='F', fill='#003399')
        else:
            self.canvas.itemconfig(cell.rect_id, fill='gray')
            self.canvas.itemconfig(cell.text_id, text='')

    def game_over(self, won):
        """
        Requires:
            - The game has ended due to either a win or loss.
            - won (bool): True if the player has won, False otherwise.
        Ensures:
            - Reveals all mines and treasures on the board.
            - Updates the visual representation to show mines and treasures.
            - Triggers the game over message to the player.
        """
        self.controller.clear_saved_game()
        for row in self.model.board:
            for cell in row:
                if cell.is_mine and not cell.is_flagged:
                    self.canvas.itemconfig(cell.rect_id, fill='#FFCCCC')
                    self.canvas.itemconfig(cell.text_id, text='M', fill='#CC0000')
                elif cell.has_treasure:
                    if cell.is_flagged:
                        self.canvas.itemconfig(cell.rect_id, fill='#CCE5FF')
                        self.canvas.itemconfig(cell.text_id, text='X', fill='#006600')
                    else:
                        self.canvas.itemconfig(cell.rect_id, fill='#CCFFCC')
                        self.canvas.itemconfig(cell.text_id, text='T', fill='#006600')
                elif not (cell.is_mine or cell.has_treasure) and cell.is_flagged:
                    self.canvas.itemconfig(cell.rect_id, fill='#CCE5FF')
                    self.canvas.itemconfig(cell.text_id, text='X', fill='red')
        self.root.update()
        self.root.after(1000, self.show_game_over_message, won)

    def show_game_over_message(self, won):
        """
        Requires:
            - The game has ended and the board has been revealed.
            - won (bool): True if the player has won, False otherwise.
        Ensures:
            - Displays a message box informing the player of the game outcome.
            - Prompts the player to play again or exit.
            - Restarts the game or quits based on the player's choice.
        """
        msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = messagebox.askyesno("Game Over", msg)
        if res:
            self.controller.restart_game()
        else:
            self.root.quit()

    def refresh_labels(self):
        """
        Requires:
            - The game state has been updated (flags placed/removed).
        Ensures:
            - Updates the labels to display the current number of flags, mines, and treasures.
        """
        self.labels["flags"].config(text="Flags: " + str(self.model.flag_count))
        self.labels["mines"].config(text="Mines: " + str(self.model.mines))
        self.labels["treasures"].config(text="Treasures: " + str(self.model.num_treasures))

    def update_timer(self):
        """
        Requires:
            - The game has started (start_time is set).
        Ensures:
            - Updates the time label every second to show the elapsed time.
        """
        if self.start_time is not None:
            delta = datetime.now() - self.start_time
            ts = str(delta).split('.')[0]
            if delta.total_seconds() < 36000:
                ts = "0" + ts
            self.labels["time"].config(text=ts)
        else:
            self.labels["time"].config(text="00:00:00")
        self.root.after(1000, self.update_timer)

    def on_canvas_click(self, event):
        """
        Requires:
            - A left-click event on the canvas.
            - The click coordinates correspond to a valid cell.
        Ensures:
            - Invokes the controller's on_click method with the appropriate cell coordinates.
        """
        x = event.y // self.CELL_SIZE
        y = event.x // self.CELL_SIZE
        if 0 <= x < self.model.size_x and 0 <= y < self.model.size_y:
            self.controller.on_click(x, y)

    def on_canvas_right_click(self, event):
        """
        Requires:
            - A right-click event on the canvas.
            - The click coordinates correspond to a valid cell.
        Ensures:
            - Invokes the controller's on_right_click method with the appropriate cell coordinates.
        """
        x = event.y // self.CELL_SIZE
        y = event.x // self.CELL_SIZE
        if 0 <= x < self.model.size_x and 0 <= y < self.model.size_y:
            self.controller.on_right_click(x, y)

    def on_quit(self):
        """
        Requires:
            - The player has chosen to quit the game.
        Ensures:
            - Saves the game state if not in testing mode.
            - Closes the game window.
        """
        if not self.model.is_test_mode:
            self.controller.save_game()
            self.root.quit()
        else:
            messagebox.showinfo("Quit", "Quit option is not available in testing mode.")

    def mainloop(self):
        """
        Requires:
            - The GUI has been fully initialized.
        Ensures:
            - Starts the Tkinter main event loop to listen for user interactions.
        """
        self.root.mainloop()

class TextView:
    def __init__(self, model, controller):
        """
        Requires:
            - model (GameModel): The game model instance.
            - controller (GameController): The game controller instance.
        Ensures:
            - Initializes the text-based interface.
            - Sets up the initial game state display.
        """
        self.model = model
        self.controller = controller
        self.start_time = self.model.start_time

    def draw_board(self):
        """
        Requires:
            - model has been initialized with mines and treasures placed.
        Ensures:
            - Continuously displays the game board and handles user input until the game ends.
        """
        while True:
            self.print_board()
            total_safe_cells = self.model.size_x * self.model.size_y - self.model.mines - self.model.num_treasures
            if self.model.clicked_count == total_safe_cells:
                self.game_over(True)
                break
            command = input("Enter command (e.g., 'r x y' to reveal, 'f x y', or 'q' to quit): ")
            if not self.process_command(command):
                break

    def print_board(self):
        """
        Requires:
            - model contains the current state of the game board.
        Ensures:
            - Prints the current state of the board to the console.
            - Displays flags, mines, treasures, and numbers indicating adjacent mines.
            - Shows the current time, flag count, mine count, and treasure count.
        """
        print("")
        for x in range(self.model.size_x):
            row = ''
            for y in range(self.model.size_y):
                cell = self.model.board[x][y]
                if cell.is_revealed:
                    if cell.is_mine:
                        row += 'M '
                    elif cell.has_treasure:
                        row += 'T '
                    elif cell.adjacent_mines > 0:
                        row += f'{cell.adjacent_mines} '
                    else:
                        row += '0 '
                elif cell.is_flagged:
                    row += 'F '
                else:
                    row += '# '
            print(row)
        if self.start_time is not None:
            delta = datetime.now() - self.start_time
            ts = str(delta).split('.')[0]
            print(f"\nTime: {ts}")
        else:
            print("\nTime: 00:00:00")
        print(f"Mines: {self.model.mines} / Treasures: {self.model.num_treasures} / Flags: {self.model.flag_count}\n")

    def process_command(self, command):
        """
        Requires:
            - command (str): User input in the format 'r x y' or 'f x y' or 'q'.
        Ensures:
            - Parses and validates the command.
            - Executes the appropriate action (reveal or flag) on the specified cell.
            - Returns True to continue the game or False to end the loop.
        """
        parts = command.strip().lower().split()
        if not parts:
            print("Invalid command. Please enter 'r x y', 'f x y', or 'q' to quit.")
            return True
        action = parts[0]
        if action == 'q':
            if not self.model.is_test_mode:
                self.controller.save_game()
                print("Game saved. Exiting.")
                exit()
            else:
                print("Quit option is not available in testing mode.")
                return True
        if len(parts) != 3:
            print("Invalid command format. Please enter 'r x y', 'f x y', or 'q' to quit.")
            return True
        action, x_str, y_str = parts
        try:
            x = int(x_str) - 1
            y = int(y_str) - 1
            if not (0 <= x < self.model.size_x and 0 <= y < self.model.size_y):
                print("Coordinates out of bounds.")
                return True
            if action == 'r':
                cell = self.model.board[x][y]
                if self.model.start_time is None:
                    self.model.start_time = datetime.now()
                    self.start_time = self.model.start_time
                if cell.is_revealed or cell.is_flagged:
                    print("Cell already revealed or flagged.")
                    return True
                self.controller.on_click(x, y)
                if cell.is_mine:
                    self.game_over(False)
                    return False
                elif cell.has_treasure:
                    self.game_over(True)
                    return False
            elif action == 'f':
                self.controller.on_right_click(x, y)
            else:
                print("Unknown action. Use 'r' to reveal, 'f' to flag, or 'q' to quit.")
        except ValueError:
            print("Invalid coordinates. Coordinates should be integers.")
        return True

    def game_over(self, won):
        """
        Requires:
            - The game has ended due to either a win or loss.
            - won (bool): True if the player has won, False otherwise.
        Ensures:
            - Reveals all mines and treasures on the board.
            - Displays the final state of the board.
            - Informs the player of the game outcome.
            - Prompts the player to play again or exit.
            - Restarts the game or exits based on the player's choice.
        """
        self.controller.clear_saved_game()
        for row in self.model.board:
            for cell in row:
                if cell.is_mine or cell.has_treasure:
                    cell.is_revealed = True
        self.print_board()
        if won:
            print("Congratulations! You found the treasure and won the game!")
        else:
            print("Game Over! You hit a mine!")
        res = input("Play again? (y/n): ")
        if res.lower() == 'y':
            print("\nStarting a new game...\n")
            self.controller.restart_game()
            self.start_time = None
            self.draw_board()
        else:
            exit()

    def reset_view(self):
        """
        Requires:
            - A new game model has been initialized.
        Ensures:
            - Resets the start time.
            - Clears any previous game state from the view.
        """
        self.start_time = self.model.start_time

def load_and_validate_test_board(file_path):
    """
    Requires:
        - file_path (str): Path to the CSV file containing the test board.
    Ensures:
        - Validates the CSV file against the specified criteria.
        - Returns a tuple (bool, str, list) indicating validity, message, and the board.
    """
    if not os.path.exists(file_path):
        return False, "File does not exist.", None
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            board = []
            for row in reader:
                if len(row) != 8:
                    return False, "Each row must have exactly 8 values.", None
                parsed_row = []
                for value in row:
                    if value not in ['0', '1', '2']:
                        return False, "Each cell must be 0, 1, or 2.", None
                    parsed_row.append(int(value))
                board.append(parsed_row)
            if len(board) != 8:
                return False, "There must be exactly 8 rows.", None
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None

    mine_count = sum(row.count(1) for row in board)
    if mine_count != 10:
        return False, f"Number of mines must be exactly 10. Found {mine_count}.", None

    for idx, row in enumerate(board):
        if row.count(1) < 1:
            return False, f"Row {idx+1} does not have at least one mine.", None
    for col in range(8):
        column = [board[row][col] for row in range(8)]
        if column.count(1) < 1:
            return False, f"Column {col+1} does not have at least one mine.", None

    diagonal_mines = sum(1 for i in range(8) if board[i][i] == 1)
    if diagonal_mines != 1:
        return False, f"There must be exactly one mine on the main diagonal. Found {diagonal_mines}.", None

    adjacent_pairs = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 1:
                if y < 7 and board[x][y+1] == 1:
                    adjacent_pairs += 1
                if x < 7 and board[x+1][y] == 1:
                    adjacent_pairs += 1
    if adjacent_pairs != 1:
        return False, f"There must be exactly one pair of adjacent mines horizontally or vertically. Found {adjacent_pairs} pairs.", None

    treasure_count = sum(row.count(2) for row in board)
    if treasure_count < 1:
        return False, "There must be at least one treasure.", None
    if treasure_count > 9:
        return False, "There must be no more than 9 treasures.", None

    return True, "Board is valid.", board

def main():
    """
    Requires:
        - User input for selecting game level and view.
    Ensures:
        - Initializes the game model based on the selected level.
        - Handles saved games and testing mode.
        - Launches the chosen view (GUI or Text) for gameplay.
        - Handles invalid user inputs by prompting again.
    """
    print("\nWelcome to Minesweeper with Hidden Treasures!\n")
    print("Choose a level:")
    print(f"1. Beginner (8x8, 10 mines, {levels['beginner']['num_treasures']} treasures)")
    print(f"2. Intermediate (16x16, 40 mines, {levels['intermediate']['num_treasures']} treasures)")
    print(f"3. Expert (30x16, 99 mines, {levels['expert']['num_treasures']} treasures)")
    level_choice = input("\nEnter the number: ").strip()
    if level_choice == '1':
        level = 'beginner'
    elif level_choice == '2':
        level = 'intermediate'
    elif level_choice == '3':
        level = 'expert'
    else:
        print("Invalid choice. Please enter '1', '2', or '3'.")
        main()
        return
    params = levels[level]

    saved_game_file = f"{level}.sav"
    model = None
    if os.path.exists(saved_game_file):
        choice = input("Do you want to continue with the previous game or start again? (c/s): ").strip().lower()
        if choice == 'c':
            with open(saved_game_file, 'rb') as f:
                model = pickle.load(f)
        elif choice == 's':
            model = None
        else:
            print("Invalid choice. Please enter 'c' or 's'.")
            main()
            return

    if level == 'beginner' and model is None:
        while True:
            test_mode_choice = input("\nWould you like to enter testing mode? (y/n): ").strip().lower()
            if test_mode_choice == 'y':
                file_path = input("Enter the path to the test board CSV file: ").strip()
                valid, message, board = load_and_validate_test_board(file_path)
                if valid:
                    treasure_count = sum(row.count(2) for row in board)
                    model = GameModel(params['size_x'], params['size_y'], params['num_mines'], treasure_count, level_name=level, test_board=board)
                    print(f"\nTest board is valid with {model.mines} mines and {model.num_treasures} treasures. Starting the game...")
                    break
                else:
                    print(f"Invalid board: {message}")
                    retry = input("Would you like to try entering testing mode again? (y/n): ").strip().lower()
                    if retry != 'y':
                        break
            elif test_mode_choice == 'n':
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    if not model:
        model = GameModel(params['size_x'], params['size_y'], params['num_mines'], params['num_treasures'], level_name=level)

    print("\nChoose a view:")
    print("1. GUI")
    print("2. Text")
    view_choice = input("\nEnter the number: ").strip()
    if view_choice == '1':
        print("")
        print("--------------------")
        print("Opening GUI View...")
        print("--------------------")
        print("")
        view = GUIView(model, None)
        controller = GameController(model, view)
        view.controller = controller
        controller.start_game()
        view.mainloop()
    elif view_choice == '2':
        print("")
        print("--------------------")
        print("Opening Text View...")
        print("--------------------")
        view = TextView(model, None)
        controller = GameController(model, view)
        view.controller = controller
        controller.start_game()
    else:
        print("\nInvalid choice. Please enter '1' for GUI or '2' for Text.")
        main()

if __name__ == "__main__":
    main()

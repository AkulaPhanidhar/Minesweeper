import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
import platform
from datetime import datetime

SIZE_X = 10
SIZE_Y = 10
CELL_SIZE = 50
MINE_PROBABILITY = 0.1

BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

class Cell:
    def __init__(self, x, y):
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
    def __init__(self, size_x, size_y, mine_probability):
        self.size_x = size_x
        self.size_y = size_y
        self.mine_probability = mine_probability
        self.board = [[Cell(x, y) for y in range(size_y)] for x in range(size_x)]
        self.mines = 0
        self.start_time = None
        self.flag_count = 0
        self.clicked_count = 0
        self.place_mines()
        self.calculate_adjacent_mines()
        self.place_treasure()

    def place_mines(self):
        for row in self.board:
            for cell in row:
                if random.uniform(0.0, 1.0) < self.mine_probability:
                    cell.is_mine = True
                    self.mines += 1

    def calculate_adjacent_mines(self):
        for row in self.board:
            for cell in row:
                cell.adjacent_mines = self.count_adjacent_mines(cell)

    def count_adjacent_mines(self, cell):
        count = 0
        for neighbor in self.get_neighbors(cell.x, cell.y):
            if neighbor.is_mine:
                count += 1
        return count

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx != 0 or dy != 0) and 0 <= nx < self.size_x and 0 <= ny < self.size_y:
                    neighbors.append(self.board[nx][ny])
        return neighbors

    def place_treasure(self):
        available_cells = [cell for row in self.board for cell in row if not cell.is_mine]
        if available_cells:
            treasure_cell = random.choice(available_cells)
            treasure_cell.has_treasure = True
            self.treasure_cell = treasure_cell

    def is_adjacent_to_treasure(self, cell):
        treasure_neighbors = self.get_neighbors(self.treasure_cell.x, self.treasure_cell.y)
        return cell in treasure_neighbors

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def start_game(self):
        self.view.draw_board()

    def on_click(self, x, y):
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
        total_cells = self.model.size_x * self.model.size_y
        if self.model.clicked_count == total_cells - self.model.mines - 1:
            self.view.game_over(True)

    def on_right_click(self, x, y):
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

    def restart_game(self):
        self.model = GameModel(self.model.size_x, self.model.size_y, self.model.mine_probability)
        self.view.model = self.model
        self.view.controller = self
        self.view.reset_view()
        self.start_game()

class GUIView:
    def __init__(self, model, controller):
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
            "flags": tk.Label(self.frame, text="Flags: 0")
        }
        self.labels["time"].pack()
        self.labels["mines"].pack(side='left')
        self.labels["flags"].pack(side='right')
        self.start_time = None
        self.canvas = tk.Canvas(self.root, width=SIZE_Y * CELL_SIZE, height=SIZE_X * CELL_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-2>", self.on_canvas_right_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.update_timer()

    def draw_board(self):
        for x in range(self.model.size_x):
            for y in range(self.model.size_y):
                cell = self.model.board[x][y]
                x1 = y * CELL_SIZE
                y1 = x * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill='gray',
                    outline='black',
                    width=1
                )
                cell.rect_id = rect_id
                cell.text_id = self.canvas.create_text(
                    x1 + CELL_SIZE / 2,
                    y1 + CELL_SIZE / 2,
                    text='',
                    font=('Helvetica', 16)
                )
        self.refresh_labels()

    def reset_view(self):
        self.canvas.delete("all")
        self.start_time = None
        self.labels["time"].config(text="00:00:00")
        self.draw_board()

    def update_cell(self, cell):
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
        msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = messagebox.askyesno("Game Over", msg)
        if res:
            self.controller.restart_game()
        else:
            self.root.quit()

    def refresh_labels(self):
        self.labels["flags"].config(text="Flags: " + str(self.model.flag_count))
        self.labels["mines"].config(text="Mines: " + str(self.model.mines))

    def update_timer(self):
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
        x = event.y // CELL_SIZE
        y = event.x // CELL_SIZE
        if 0 <= x < self.model.size_x and 0 <= y < self.model.size_y:
            self.controller.on_click(x, y)

    def on_canvas_right_click(self, event):
        x = event.y // CELL_SIZE
        y = event.x // CELL_SIZE
        if 0 <= x < self.model.size_x and 0 <= y < self.model.size_y:
            self.controller.on_right_click(x, y)

    def mainloop(self):
        self.root.mainloop()

class TextView:
    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.start_time = None

    def draw_board(self):
        while True:
            self.print_board()
            total_cells = self.model.size_x * self.model.size_y
            if self.model.clicked_count == total_cells - self.model.mines - 1:
                self.game_over(True)
                break
            command = input("Enter command (e.g., 'r x y' to reveal or 'f x y'). Coordinates range from 1 to 10: ")
            if not self.process_command(command):
                break

    def print_board(self):
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
        print(f"\nFlags: {self.model.flag_count} / Mines: {self.model.mines}")
        if self.start_time is not None:
            delta = datetime.now() - self.start_time
            ts = str(delta).split('.')[0]
            print(f"Time: {ts}\n")
        else:
            print("Time: 00:00:00\n")

    def process_command(self, command):
        parts = command.strip().lower().split()
        if len(parts) != 3:
            print("Invalid command format. Please enter 'r x y' or 'f x y'. Coordinates range from 1 to 10.")
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
                print("Unknown action. Use 'r' to reveal or 'f' to flag.")
        except ValueError:
            print("Invalid coordinates. Coordinates should be integers.")
        return True

    def game_over(self, won):
        self.print_board()
        if won:
            print("Congratulations! You found the treasure and won the game!")
        else:
            print("Game Over! You hit a mine!")
        res = input("Play again? (y/n): ")
        if res.lower() == 'y':
            self.controller.restart_game()
            self.start_time = None
            self.draw_board()
        else:
            exit()

    def reset_view(self):
        self.start_time = None

def main():
    print("\nChoose a view:")
    print("1. GUI")
    print("2. Text")
    view_choice = input("Enter the number: ").strip()
    model = GameModel(SIZE_X, SIZE_Y, MINE_PROBABILITY)
    if view_choice == '1':
        print("")
        print("-" * 20)
        print("Opening GUI View...")
        print("-" * 20)
        print("")
        view = GUIView(model, None)
        controller = GameController(model, view)
        view.controller = controller
        controller.start_game()
        view.mainloop()
    elif view_choice == '2':
        print("")
        print("-" * 20)
        print("Opening Text View...")
        print("-" * 20)
        view = TextView(model, None)
        controller = GameController(model, view)
        view.controller = controller
        controller.start_game()
    else:
        print("Invalid choice. Please enter '1' for GUI or '2' for Text.")
        main()

if __name__ == "__main__":
    main()

import tkinter as tk
import random
import os
import time

initial = 0


class EndWindow(tk.Toplevel):
    def __init__(self, board, controller):
        tk.Toplevel.__init__(self)

        final = time.time()
        elapsed = int(final-initial)

        self.grab_set()
        self.board = board
        self.controller = controller
        self.title("")
        self.resizable(0, 0)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(1)

        self.message = tk.Label(self.container, font=("Courier", 12, 'bold'), padx=10, pady=20)
        if board.model.game_over is True:
            self.container.configure(bg='#FF6347')
            self.message.configure(bg='#FF6347')
            self.message.configure(text="Game Over! You exploded all the mines!")
        else:
            self.container.configure(bg='#00FF7F')
            self.message.configure(bg='#00FF7F')
            self.message.configure(text=f"Congratulations! You located all the mines in {elapsed} secs!")

        self.message.grid(row=0, column=0, columnspan=2)

        self.restart_button = tk.Button(self.container, text="RESTART", font=("Courier", 14),  command=self.restart)
        self.restart_button.grid(row=1, column=0, sticky="wens", padx=10, pady=20)
        self.menu_button = tk.Button(self.container, text="MENU", font=("Courier", 14), command=self.menu)
        self.menu_button.grid(row=1, column=1, sticky="wens", padx=10, pady=20)

    def restart(self):
        self.destroy()
        self.board.destroy()
        self.controller.create_frame(Board)

    def menu(self):
        self.destroy()
        self.board.destroy()
        self.controller.create_frame(Menu)


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.resizable(0, 0)
        self.title("Minesweeper w/ Python")
        self.container = tk.Frame(self)

        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.create_frame(Menu)

    def show_frame(self, screen_name):
        frame = self.frames[screen_name]
        frame.tkraise()

    def create_frame(self, Screen):
        screen_name = Screen.__name__
        frame = Screen(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames[screen_name] = frame
        self.show_frame(screen_name)


class Menu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#F0DEB4')
        self.controller = controller
        self.v = tk.IntVar()
        self.v.set(1)

        self.title_canvas = tk.Canvas(self, width=250, height=50, bg='#F0DEB4', highlightthickness=0)
        self.title_canvas.pack(padx=24, pady=24)
        self.title_canvas.create_text(125, 25, font=("Courier", 24), text="Minesweeper")

        self.menu_canvas = tk.Canvas(self, width=175, height=150)
        self.menu_canvas.pack(pady=(0, 24))

        self.difficulty_easy = tk.Radiobutton(self.menu_canvas, text="Easy     9x9", font=("Courier", 12), variable=self.v,
                                              value=1)
        self.difficulty_medium = tk.Radiobutton(self.menu_canvas, text="Medium  16x16", font=("Courier", 12),
                                                variable=self.v, value=2)
        self.difficulty_hard = tk.Radiobutton(self.menu_canvas, text="Hard    16x30", font=("Courier", 12), variable=self.v,
                                              value=3)
        self.play = tk.Button(self.menu_canvas, text="START", font=("Courier", 14), command=lambda: controller.create_frame(Board))

        self.menu_window = self.menu_canvas.create_window(8, 25, anchor='w', window=self.difficulty_easy)
        self.menu_window = self.menu_canvas.create_window(8, 50, anchor='w', window=self.difficulty_medium)
        self.menu_window = self.menu_canvas.create_window(8, 75, anchor='w', window=self.difficulty_hard)
        self.menu_window = self.menu_canvas.create_window(50, 120, anchor='w', window=self.play)


class Board(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#F0DEB4')

        global initial
        initial = time.time()
        self.controller = controller
        self.flag_img = tk.PhotoImage(file="flag.png")
        self.reveal_counter = 0

        difficulty = controller.frames["Menu"].v.get()

        if difficulty == 1:
            self.row = 9
            self.col = 9
            self.mine = 10
        elif difficulty == 2:
            self.row = 16
            self.col = 16
            self.mine = 40
        else:
            self.row = 16
            self.col = 30
            self.mine = 99

        self.model = Map(self.row, self.col, self.mine) # create model (data structure) for game
        self.model.generate_array()

        self.rowconfigure(self.row, weight=1)
        self.columnconfigure(self.col, weight=1)

        for c in range(self.col):
            for r in range(self.row):
                f = tk.Frame(self, height=32, width=32)
                f.grid_propagate(False)
                f.columnconfigure(0, weight=1)
                f.rowconfigure(0, weight=1)

                tile = tk.Button(f, bg=None, command=lambda row=r, col=c: self.click_left(row, col))
                tile.grid(row=0, column=0, sticky="wens")
                tile.bind("<Button-3>", lambda event, row=r, col=c: self.click_right(event, row, col))

                f.grid(row=r, column=c, padx=2, pady=2)

    def click_left(self, row, col):
        if self.model.array[row][col].mine is True:
            self.model.game_over = True
            reveal_set = self.model.mines
            self.reveal(reveal_set)
            window = EndWindow(self, self.controller)

        else:
            if self.model.array[row][col].proximity == 0:
                safe_set = self.model.locate_safe((row, col), set())
                reveal_set = self.model.reveal_neighbours(safe_set)
            else:
                reveal_set = {(row, col)}

            self.reveal(reveal_set)

            if self.model.is_game_won():
                window = EndWindow(self, self.controller)

    def click_right(self, event, row, col):
        button = event.widget
        if self.model.flag_tile(row, col) is True:
            button.config(state='disabled', image=self.flag_img)
        else:
            button.config(state='normal', image="")

    def reveal(self, reveal_set):
        current_dir = os.getcwd()
        folder_dir = os.path.join(current_dir, "num_img")

        proximity_image = {
            0: "empty.png",
            1: "num1.png",
            2: "num2.png",
            3: "num3.png",
            4: "num4.png",
            5: "num5.png",
            6: "num6.png",
            7: "num7.png",
            8: "num8.png"
        }

        for tile in reveal_set:
            r, c = tile

            if self.model.game_over is True:
                img = tk.PhotoImage(file="mine.png")
            else:
                proximity = self.model.array[r][c].proximity
                img = tk.PhotoImage(file=os.path.join(folder_dir, proximity_image[proximity]))

            frame = self.grid_slaves(r, c)[0]
            button = frame.grid_slaves(0, 0)[0]
            button.destroy()

            image_box = tk.Label(frame, image=img)
            image_box.image = img
            image_box.grid(row=0, column=0, sticky="wens")

            self.model.unpressed.discard(tile)


class Map:
    # can calculate tile coords and proximity based on 2D List of Tile Object
    def __init__(self, rows, cols, mines):
        self.mines=set()
        self.array = []  # array[ROW][COL]
        self.unpressed = set()
        self.game_over = False
        self.row = rows
        self.col = cols
        self.mine_total = mines

    def generate_array(self):
        self.array = [[Tile() for j in range(self.col)] for i in range(self.row)]  # 2d array to store Tile objects
        coord_list = [(r, c) for c in range(self.col) for r in range(self.row)]  # list of available mine coordinates

        for mine in range(self.mine_total):   # randomly select mine locations
            random.shuffle(coord_list)
            r, c = coord_list.pop()
            self.mines.add((r, c))
            self.array[r][c].mine = True

            nearby_set = self.locate_nearby(r, c)

            for nearby_mine in nearby_set:  # iterate over each nearby mine to increase proximity attribute
                a, b = nearby_mine
                self.array[a][b].proximity += 1

        self.unpressed = set(coord_list)

    def locate_nearby(self, row, col):
        nearby_set = {(r, c) for c in range(max(0, col - 1), min(self.col, col + 2)) for r in range(max(0, row - 1), min(self.row, row + 2))}
        return nearby_set

    def locate_open_adjacent(self, row, col):
        adjacent_set = {(row - 1, col), (row, col - 1), (row, col), (row, col + 1), (row + 1, col)}
        open_set = adjacent_set.intersection(self.locate_nearby(row, col))

        for tile in open_set.copy():
            r, c = tile
            if self.array[r][c].proximity != 0:
                open_set.remove(tile)

        return open_set

    def locate_safe(self, tile, safe_tiles):
        r, c = tile
        open_set = self.locate_open_adjacent(r, c)
        if tile in safe_tiles or tile not in open_set:
            return {}
        else:
            safe_tiles.add(tile)

        safe_tiles.union(self.locate_safe((r - 1, c), safe_tiles))
        safe_tiles.union(self.locate_safe((r + 1, c), safe_tiles))
        safe_tiles.union(self.locate_safe((r, c - 1), safe_tiles))
        safe_tiles.union(self.locate_safe((r, c + 1), safe_tiles))

        return safe_tiles

    def reveal_neighbours(self, safe_tiles):
        reveal_set=set()
        for tile in safe_tiles:
            r, c = tile
            reveal_set.update(self.locate_nearby(r, c))

        for tile in reveal_set:
            r, c = tile
            self.array[r][c].reveal = True

        return reveal_set

    def reveal_mine(self):
        for mine in self.mines:
            r, c = mine
            self.array[r][c].reveal = True

    def flag_tile(self, row, col):  # update gui/change array[][].flag = True
        if self.array[row][col].flag is False:
            self.array[row][col].flag = True
            return True
        else:
            self.array[row][col].flag = False
            return False

    def is_game_won(self):
        return len(self.unpressed) == 0


class Tile:
    reveal = False
    mine = False
    flag = False
    proximity = 0


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()


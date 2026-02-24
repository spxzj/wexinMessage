import random
import tkinter as tk


CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
UPDATE_DELAY_MS = 120


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("贪吃蛇")

        canvas_width = GRID_WIDTH * CELL_SIZE
        canvas_height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#111")
        self.canvas.pack(padx=10, pady=10)

        self.info_label = tk.Label(root, text="方向键控制，空格暂停/继续，R 重新开始", font=("Arial", 11))
        self.info_label.pack(pady=(0, 8))

        self.score_label = tk.Label(root, text="分数: 0", font=("Arial", 12, "bold"))
        self.score_label.pack(pady=(0, 10))

        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.paused = False
        self.game_over = False
        self.after_id = None

        self.reset_game_state()
        self.bind_keys()
        self.draw()
        self.schedule_next_tick()

    def reset_game_state(self) -> None:
        mid_x = GRID_WIDTH // 2
        mid_y = GRID_HEIGHT // 2
        self.snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.paused = False
        self.food = self.spawn_food()
        self.update_score_label()

    def bind_keys(self) -> None:
        self.root.bind("<Up>", lambda _: self.set_direction((0, -1)))
        self.root.bind("<Down>", lambda _: self.set_direction((0, 1)))
        self.root.bind("<Left>", lambda _: self.set_direction((-1, 0)))
        self.root.bind("<Right>", lambda _: self.set_direction((1, 0)))
        self.root.bind("<space>", lambda _: self.toggle_pause())
        self.root.bind("r", lambda _: self.restart())
        self.root.bind("R", lambda _: self.restart())

    def set_direction(self, new_direction: tuple[int, int]) -> None:
        if self.game_over:
            return

        current_dx, current_dy = self.direction
        new_dx, new_dy = new_direction
        # 阻止直接反向，避免“秒死”
        if (new_dx, new_dy) == (-current_dx, -current_dy):
            return

        self.pending_direction = new_direction

    def toggle_pause(self) -> None:
        if self.game_over:
            return
        self.paused = not self.paused
        if not self.paused and self.after_id is None:
            self.schedule_next_tick()
        self.draw()

    def restart(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.reset_game_state()
        self.draw()
        self.schedule_next_tick()

    def spawn_food(self) -> tuple[int, int]:
        occupied = set(self.snake)
        all_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)]
        candidates = [cell for cell in all_cells if cell not in occupied]
        return random.choice(candidates)

    def update_score_label(self) -> None:
        self.score_label.config(text=f"分数: {self.score}")

    def schedule_next_tick(self) -> None:
        self.after_id = self.root.after(UPDATE_DELAY_MS, self.tick)

    def tick(self) -> None:
        self.after_id = None

        if self.paused or self.game_over:
            self.draw()
            if not self.game_over:
                self.schedule_next_tick()
            return

        self.direction = self.pending_direction
        dx, dy = self.direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        if self.hit_wall(new_head) or self.hit_self(new_head):
            self.game_over = True
            self.draw()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.update_score_label()
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.draw()
        self.schedule_next_tick()

    def hit_wall(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

    def hit_self(self, new_head: tuple[int, int]) -> bool:
        return new_head in self.snake

    def draw_cell(self, x: int, y: int, color: str) -> None:
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#222")

    def draw(self) -> None:
        self.canvas.delete("all")

        for x in range(GRID_WIDTH):
            self.canvas.create_line(x * CELL_SIZE, 0, x * CELL_SIZE, GRID_HEIGHT * CELL_SIZE, fill="#1b1b1b")
        for y in range(GRID_HEIGHT):
            self.canvas.create_line(0, y * CELL_SIZE, GRID_WIDTH * CELL_SIZE, y * CELL_SIZE, fill="#1b1b1b")

        food_x, food_y = self.food
        self.draw_cell(food_x, food_y, "#e74c3c")

        for i, (x, y) in enumerate(self.snake):
            color = "#2ecc71" if i == 0 else "#27ae60"
            self.draw_cell(x, y, color)

        if self.paused:
            self.show_center_text("已暂停\n按空格继续", "#f1c40f")
        elif self.game_over:
            self.show_center_text("游戏结束\n按 R 重新开始", "#ff7675")

    def show_center_text(self, text: str, color: str) -> None:
        self.canvas.create_text(
            GRID_WIDTH * CELL_SIZE // 2,
            GRID_HEIGHT * CELL_SIZE // 2,
            text=text,
            fill=color,
            font=("Arial", 24, "bold"),
            justify="center",
        )


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

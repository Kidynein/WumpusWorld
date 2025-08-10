import pygame
from enum import Enum
from movingwumpus import MovingWumpusModule
class GameMode(Enum):
    AUTO = "Auto"
    STEP = "Step"
class GUI:
    def __init__(self, world, agent):
        pygame.init()
        self.world = world
        self.agent = agent
        self.agent_type = "Hybrid"
        self.moving_wumpus = MovingWumpusModule(world)  # Initialize the moving Wumpus module
        # Grid and UI sizing
        self.GRID_SIZE = world.grid_size
        self.MARGIN = 50
        self.UI_WIDTH = 300
        self.BUTTON_HEIGHT = 40
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 700
        available_grid_width = self.WINDOW_WIDTH - self.UI_WIDTH - 2 * self.MARGIN
        available_grid_height = self.WINDOW_HEIGHT - 2 * self.MARGIN - 100
        self.CELL_SIZE = min(available_grid_width // self.GRID_SIZE,
                             available_grid_height // self.GRID_SIZE)
        # Pygame setup
        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Wumpus World")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_BG = (30, 30, 30)
        self.LIGHT_DARK_BG = (50, 50, 50)
        self.LIGHT_GRAY = (170, 170, 170)
        self.GREEN = (0, 255, 0)
        self.LIGHT_GREEN = (150, 255, 150)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)

        # Initial mode and buttons
        self.mode = GameMode.STEP
        self.buttons = self._create_buttons()

        # Load hình ảnh và scale theo CELL_SIZE
        self.agent_img = pygame.transform.scale(pygame.image.load("assets/agent.png"), (self.CELL_SIZE, self.CELL_SIZE))
        self.wumpus_img = pygame.transform.scale(pygame.image.load("assets/wumpus.png"), (self.CELL_SIZE, self.CELL_SIZE))
        self.gold_img = pygame.transform.scale(pygame.image.load("assets/gold.png"), (int(self.CELL_SIZE * 0.8), int(self.CELL_SIZE * 0.8)))
        self.pit_img = pygame.transform.scale(pygame.image.load("assets/pit.png"), (self.CELL_SIZE, self.CELL_SIZE))
        self.block_img = pygame.transform.scale(pygame.image.load("assets/floor.jpg"), (self.CELL_SIZE, self.CELL_SIZE))
        self.breeze_img = pygame.transform.scale(pygame.image.load("assets/breeze.png"), (int(self.CELL_SIZE * 0.5), int(self.CELL_SIZE * 0.5)))
        self.stench_img = pygame.transform.scale(pygame.image.load("assets/stench.png"), (int(self.CELL_SIZE * 0.5), int(self.CELL_SIZE * 0.5)))

        # NEW: Toggle for showing actual pit/Wumpus icons
        self.show_dangers = False
        self.show_gold = False
        self.show_config_popup = False
        self.ADVANCE_MODE = False
    def _update(self, new_world, new_agent):
        """Update the GUI with a new world state."""
        self.world = new_world
        self.agent = new_agent
        self.buttons = self._create_buttons()
        available_grid_width = self.WINDOW_WIDTH - self.UI_WIDTH - 2 * self.MARGIN
        available_grid_height = self.WINDOW_HEIGHT - 2 * self.MARGIN - 100
        self.GRID_SIZE = new_world.grid_size
        self.CELL_SIZE = min(available_grid_width // self.GRID_SIZE,
                             available_grid_height // self.GRID_SIZE)
        # Load hình ảnh và scale theo CELL_SIZE
        self.agent_img = pygame.transform.scale(pygame.image.load("assets/agent.png"), (self.CELL_SIZE, self.CELL_SIZE))
        self.wumpus_img = pygame.transform.scale(pygame.image.load("assets/wumpus.png"), (self.CELL_SIZE, self.CELL_SIZE))
        self.gold_img = pygame.transform.scale(pygame.image.load("assets/gold.png"), (int(self.CELL_SIZE * 0.8), int(self.CELL_SIZE * 0.8)))
        self.pit_img = pygame.transform.scale(pygame.image.load("assets/pit.png"), (self.CELL_SIZE, self.CELL_SIZE))
        self.block_img = pygame.transform.scale(pygame.image.load("assets/floor.jpg"), (self.CELL_SIZE, self.CELL_SIZE))
        self.breeze_img = pygame.transform.scale(pygame.image.load("assets/breeze.png"), (int(self.CELL_SIZE * 0.5), int(self.CELL_SIZE * 0.5)))
        self.stench_img = pygame.transform.scale(pygame.image.load("assets/stench.png"), (int(self.CELL_SIZE * 0.5), int(self.CELL_SIZE * 0.5)))
    def _flip_y(self, row_index):
        """Chuyển chỉ số hàng thành toạ độ y đảo ngược."""
        return self.MARGIN + (self.GRID_SIZE - 1 - row_index) * self.CELL_SIZE
    def _create_buttons(self):
        """Define interactive buttons with positions and actions."""
        base_y = self.GRID_SIZE * self.CELL_SIZE + 2 * self.MARGIN
        configs = [
            ("Step Mode", "step_mode"),
            ("Auto Mode", "auto_mode"),
            ("Show All", "toggle_all"),
            ("Reset Game", "reset_game"),
            ("New Seed", "new_seed"),
            ("Advance", "advance"),
            (f"Agent: {self.agent_type}", "switch_agent"),
        ]
        buttons = []
        for idx, (label, action) in enumerate(configs):
            x = self.MARGIN + (idx % 4) * 160
            y = base_y + (idx // 4) * (self.BUTTON_HEIGHT + 5)
            rect = pygame.Rect(x, y, 150, self.BUTTON_HEIGHT)
            buttons.append({"rect": rect, "label": label, "action": action})
        return buttons

    def draw_grid(self):
        """Draw the game grid with enhanced cell visualization and icons."""
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                x = self.MARGIN + j * self.CELL_SIZE
                y = self._flip_y(i)
                cell_pos = (i, j)
                cell_data = self.world.world[i][j]

                if (
                    cell_pos not in self.agent.unsafe_cells
                    and cell_pos not in self.agent.warning_cells
                    and cell_pos not in self.agent.safe_cells
                ):
                    self.screen.blit(self.block_img, (x, y))
                else:
                    if cell_pos in self.agent.unsafe_cells:
                        color = self.RED
                    elif cell_pos in self.agent.warning_cells:
                        color = self.YELLOW
                    else:
                        color = (
                            self.GREEN
                            if cell_pos in self.agent.visited_cells
                            else self.LIGHT_GREEN
                        )
                    pygame.draw.rect(
                        self.screen, color, (x, y, self.CELL_SIZE, self.CELL_SIZE)
                    )

                pygame.draw.rect(
                    self.screen, self.WHITE, (x, y, self.CELL_SIZE, self.CELL_SIZE), 2
                )

                if self.show_dangers:
                    if cell_data["pit"]:
                        self.screen.blit(self.pit_img, (x, y))
                    elif cell_data["wumpus"]:
                        self.screen.blit(self.wumpus_img, (x, y))

                if cell_pos == self.world.agent_pos:
                    ax = x + (self.CELL_SIZE - self.agent_img.get_width()) // 2
                    ay = y + (self.CELL_SIZE - self.agent_img.get_height()) // 2
                    self.screen.blit(self.agent_img, (ax, ay))
                    self._draw_agent_direction(x, y)

                if cell_data["gold"] and (self.show_gold or cell_pos in self.agent.visited_cells):
                    gx = x + (self.CELL_SIZE - self.gold_img.get_width()) // 2
                    gy = y + (self.CELL_SIZE - self.gold_img.get_height()) // 2
                    self.screen.blit(self.gold_img, (gx, gy))

                if cell_pos == self.world.agent_pos or cell_pos in self.agent.visited_cells:
                    if cell_pos in self.agent.breeze_cells:
                        self.screen.blit(self.breeze_img, (x, y))
                    if cell_pos in self.agent.stench_cells:
                        self.screen.blit(self.stench_img, (x, y + self.CELL_SIZE/2))

    def _draw_agent_direction(self, x: int, y: int):
        """Draw a small triangle indicating agent’s facing direction."""
        center_x = x + self.CELL_SIZE // 2
        center_y = y + self.CELL_SIZE // 2
        dir = self.world.agent_dir
        if dir == "up":
            pts = [
                (center_x, center_y - 22),
                (center_x - 8, center_y - 8),
                (center_x + 8, center_y - 8),
            ]
        elif dir == "down":
            pts = [
                (center_x, center_y + 22),
                (center_x - 8, center_y + 8),
                (center_x + 8, center_y + 8),
            ]
        elif dir == "left":
            pts = [
                (center_x - 22, center_y),
                (center_x - 8, center_y - 8),
                (center_x - 8, center_y + 8),
            ]
        else:  # right
            pts = [
                (center_x + 22, center_y),
                (center_x + 8, center_y - 8),
                (center_x + 8, center_y + 8),
            ]
        pygame.draw.polygon(self.screen, self.BLUE, pts)

    def draw_ui_panel(self):
        """Draw the right‐hand UI panel showing mode, status, inventory, and knowledge."""
        px = self.GRID_SIZE * self.CELL_SIZE + 2 * self.MARGIN
        py = self.MARGIN
        panel_w = self.UI_WIDTH - 20
        panel_h = self.WINDOW_HEIGHT - 2 * self.MARGIN - 100

        # Panel background and border
        pygame.draw.rect(self.screen, self.DARK_BG, (px, py, panel_w, panel_h))
        pygame.draw.rect(self.screen, self.WHITE, (px, py, panel_w, panel_h), 2)

        y = py + 10
        # Mode
        mode_text = self.font.render(f"Mode: {self.mode.value}", True, self.WHITE)
        self.screen.blit(mode_text, (px + 10, y))
        y += 30

        # Game status
        status = self.world.is_game_over(self.agent)
        color = (
            self.GREEN
            if status == "win"
            else self.RED
            if status == "lose"
            else self.WHITE
        )
        status_text = self.font.render(f"Status: {status}", True, color)
        self.screen.blit(status_text, (px + 10, y))
        y += 25

        # Inventory (gold and arrow)
        gold_text = self.small_font.render(
            f"Has Gold: {self.world.has_gold}", True, self.WHITE
        )
        arrow_text = self.small_font.render(
            f"Has Arrow: {self.world.has_arrow}", True, self.WHITE
        )
        score_text = self.small_font.render(
            f"Score: {self.world.score}", True, self.WHITE
        )
        self.screen.blit(gold_text, (px + 10, y))
        y += 20
        self.screen.blit(arrow_text, (px + 10, y))
        y += 20
        self.screen.blit(score_text, (px + 10, y))
        y += 25

        # Cell counts
        counts = f"Safe: {len(self.agent.safe_cells)} | Warning: {len(self.agent.warning_cells)} | Danger: {len(self.agent.unsafe_cells)}"
        counts_text = self.small_font.render(counts, True, self.WHITE)
        self.screen.blit(counts_text, (px + 10, y))
        y += 25

        # Percepts
        perc_title = self.font.render("Percepts:", True, self.WHITE)
        self.screen.blit(perc_title, (px + 10, y))
        y += 25
        for p, val in self.world.percepts.items():
            if val:
                p_text = self.small_font.render(f"• {p}", True, self.WHITE)
                self.screen.blit(p_text, (px + 15, y))
                y += 18
        action_title = self.font.render("Action:", True, self.WHITE)
        self.screen.blit(action_title, (px + 10, y))
        action_text = self.font.render(f"{self.agent.last_action}", True, self.WHITE)
        self.screen.blit(action_text, (px + 90, y))
        y += 30

        # Knowledge Base (last few entries)
        kb_title = self.font.render("Knowledge Base:", True, self.WHITE)
        self.screen.blit(kb_title, (px + 10, y))
        y += 25
        for entry in self.agent.knowledge_base[-10:]:
            if y < py + panel_h - 50:
                txt = entry if len(entry) <= 28 else entry[:28] + "..."
                kb_text = self.small_font.render(txt, True, self.WHITE)
                self.screen.blit(kb_text, (px + 10, y))
                y += 16

    def draw_buttons(self):
        """Render interactive buttons at the bottom."""
        for btn in self.buttons:
            rect = btn["rect"]
            action = btn["action"]

            # Default button color
            color = self.LIGHT_DARK_BG

            # Highlight mode buttons
            if action == "auto_mode" and self.mode == GameMode.AUTO:
                color = self.GREEN
            elif action == "toggle_all" and (self.show_gold or self.show_dangers):
                color = self.GREEN
            elif action == "step_mode" and self.mode == GameMode.STEP:
                color = self.GREEN
            elif action == "advance" and self.ADVANCE_MODE:
                color = self.GREEN
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.WHITE, rect, 2)
            label = self.small_font.render(btn["label"], True, self.WHITE)
            lbl_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, lbl_rect)


    def handle_button_click(self, mouse_pos):
        """
        Return a command string if a button was clicked:
        'auto_mode', 'toggle_all', 'reset_game', or 'new_seed'.
        Otherwise, return None.
        """
        for btn in self.buttons:
            if btn["rect"].collidepoint(mouse_pos):
                action = btn["action"]
                if action in ("auto_mode", "step_mode"):
                    if action == "auto_mode":
                        self.mode = GameMode.AUTO
                    elif action == "step_mode":
                        self.mode = GameMode.STEP
                    return None
                elif action == "toggle_all":
                    self.show_gold = not self.show_gold
                    self.show_dangers = not self.show_dangers
                    return None
                elif action == "advance":
                    self.ADVANCE_MODE = not self.ADVANCE_MODE
                    return None
                elif action == "switch_agent":
                    self.agent_type = "Random" if self.agent_type == "Hybrid" else "Hybrid"
                    self.buttons = self._create_buttons()  # Cập nhật lại tên nút
                    return "switch_agent"
                return action
        return None

    def render(self):
        """Clear the screen and redraw the entire UI (grid, panel, buttons)."""
        self.screen.fill(self.DARK_BG)
        self.draw_grid()
        self.draw_ui_panel()
        self.draw_buttons()
        pygame.display.flip()


    def handle_game_over_click(self, pos):
        if self.reset_button.collidepoint(pos):
            return "reset_game"
        elif self.new_game_button.collidepoint(pos):
            return "new_seed"
        return None

import random
from enum import Enum
from typing import Dict, List, Tuple

class WumpusWorld:
    def __init__(self, seed=36):
        self.grid_size = 5
        self.agent_pos = (0, 0)
        self.agent_dir = "right"
        self.has_gold = False
        self.has_arrow = True
        self.wumpus_alive = True
        self.game_over_state = None
        self.seed = seed
        self.score = 0
        random.seed(self.seed)
        self.world = self._generate_world()
        self.percepts = self._update_percepts()

    def _generate_world(self):
        world = [[{"pit": False, "wumpus": False, "gold": False} for _ in range(self.grid_size)]
                 for _ in range(self.grid_size)]

        # Place Wumpus (exactly one, not at start)
        while True:
            wx = random.randint(0, self.grid_size - 1)
            wy = random.randint(0, self.grid_size - 1)
            if (wx, wy) != (0, 0):
                world[wx][wy]["wumpus"] = True
                break

        # Place Gold (exactly one, not at start or Wumpus)
        while True:
            gx = random.randint(0, self.grid_size - 1)
            gy = random.randint(0, self.grid_size - 1)
            if (gx, gy) not in [(0, 0), (wx, wy)]:
                world[gx][gy]["gold"] = True
                break

        # Place exactly 3 pits (not at start, Wumpus, or Gold)
        all_positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size)]
        forbidden = {(0, 0), (wx, wy), (gx, gy)}
        available = [pos for pos in all_positions if pos not in forbidden]
        pit_positions = random.sample(available, min(3, len(available)))
        for (px, py) in pit_positions:
            world[px][py]["pit"] = True

        return world

    def _update_percepts(self):
        x, y = self.agent_pos
        percepts = {
            "stench": False,
            "breeze": False,
            "glitter": False,
            "bump": False,
            "scream": False
        }

        # Check for stench (adjacent Wumpus) and breeze (adjacent pit)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                cell = self.world[nx][ny]
                if cell["wumpus"] and self.wumpus_alive:
                    percepts["stench"] = True
                if cell["pit"]:
                    percepts["breeze"] = True

        # Check for glitter (gold in current cell)
        if self.world[x][y]["gold"]:
            percepts["glitter"] = True

        return percepts

    def get_neighbors(self, pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                neighbors.append((nx, ny))
        return neighbors

    def move_forward(self):
        x, y = self.agent_pos
        new_x, new_y = x, y

        if self.agent_dir == "up":
            new_x += 1
        elif self.agent_dir == "down":
            new_x -= 1
        elif self.agent_dir == "left":
            new_y -= 1
        elif self.agent_dir == "right":
            new_y += 1

        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.agent_pos = (new_x, new_y)
            self.percepts = self._update_percepts()
            return True

        # Bump if against wall
        self.percepts["bump"] = True
        return False

    def turn_left(self):
        directions = ["up", "left", "down", "right"]
        idx = directions.index(self.agent_dir)
        self.agent_dir = directions[(idx + 1) % 4]
        # Percepts do not change when only turning.

    def turn_right(self):
        directions = ["up", "right", "down", "left"]
        idx = directions.index(self.agent_dir)
        self.agent_dir = directions[(idx + 1) % 4]
        # Percepts do not change when only turning.

    def shoot_arrow(self):
        if not self.has_arrow:
            return False

        self.has_arrow = False
        x, y = self.agent_pos
        hit = False

        if self.agent_dir == "up":
            for i in range(x - 1, -1, -1):
                if self.world[i][y]["wumpus"]:
                    hit = True
                    break
        elif self.agent_dir == "down":
            for i in range(x + 1, self.grid_size):
                if self.world[i][y]["wumpus"]:
                    hit = True
                    break
        elif self.agent_dir == "left":
            for j in range(y - 1, -1, -1):
                if self.world[x][j]["wumpus"]:
                    hit = True
                    break
        elif self.agent_dir == "right":
            for j in range(y + 1, self.grid_size):
                if self.world[x][j]["wumpus"]:
                    hit = True
                    break

        if hit:
            self.wumpus_alive = False
            self.percepts["scream"] = True
            return True

        return False

    def grab_gold(self):
        x, y = self.agent_pos
        if self.world[x][y]["gold"]:
            self.has_gold = True
            self.world[x][y]["gold"] = False
            self.percepts["glitter"] = False
            return True
        return False

    def climb_out(self):
        # Climbing out is only allowed at the starting position (0, 0)
        if self.agent_pos != (0, 0):
            return False
        if not self.has_gold:
            self.game_over_state = "lose"
            return False
        # If the agent is at (0, 0) and has gold, the game is won
        self.game_over_state = "win"
        self.score += 1000
        return True

    def is_game_over(self):
        if self.game_over_state is not None:
            return self.game_over_state

        x, y = self.agent_pos
        cell = self.world[x][y]

        # Check for death by pit or alive Wumpus
        if cell["pit"] or (cell["wumpus"] and self.wumpus_alive):
            self.game_over_state = "lose"
            return "lose"

        # Check win condition: grabbed gold and returned to start
        if self.agent_pos == (0, 0) and self.has_gold:
            self.game_over_state = "win"
            return "win"
        return "continue"
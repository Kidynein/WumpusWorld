import random
from enum import Enum
from typing import Dict, List, Tuple
class WumpusWorld:
    def __init__(self, world_size = 8, k = 2, p = 0.2, seed=36):
        self.grid_size = world_size
        self.agent_pos = (0, 0)
        self.agent_dir = "right"
        self.has_gold = False
        self.has_arrow = True
        self.game_over_state = None
        self.wumpus_alive = True
        self.seed = seed
        self.score = 0
        self.K = k
        self.pit_prob = p
        random.seed(self.seed)
        self.world = self._generate_world()
        self.percepts = self._update_percepts()

    def _generate_world(self):
        world = [[{"pit": False, "wumpus": False, "gold": False} for _ in range(self.grid_size)]
                for _ in range(self.grid_size)]

        # Place K Wumpus (not at (0,0), no duplicates)
        placed_wumpus = 0
        while placed_wumpus < self.K:
            wx = random.randint(0, self.grid_size - 1)
            wy = random.randint(0, self.grid_size - 1)
            if (wx, wy) != (0, 0) and not world[wx][wy]["wumpus"]:
                world[wx][wy]["wumpus"] = True
                placed_wumpus += 1

        # Place Gold (not with pit or wumpus; may be at (0,0))
        while True:
            gx = random.randint(0, self.grid_size - 1)
            gy = random.randint(0, self.grid_size - 1)
            if not world[gx][gy]["wumpus"] and not world[gx][gy]["pit"]:
                world[gx][gy]["gold"] = True
                break

        # Place pits with probability p (not at (0,0), not where wumpus or gold is)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if (i, j) != (0, 0) and not world[i][j]["wumpus"] and not world[i][j]["gold"]:
                    if random.random() < self.pit_prob:
                        world[i][j]["pit"] = True

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
                if cell["wumpus"]:
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
            self.score -= 1
            return True

        # Bump nếu chạm wall
        self.percepts["bump"] = True
        return False

    def turn_left(self):
        directions = ["up", "left", "down", "right"]
        idx = directions.index(self.agent_dir)
        self.agent_dir = directions[(idx + 1) % 4]
        self.score -= 1

    def turn_right(self):
        directions = ["up", "right", "down", "left"]
        idx = directions.index(self.agent_dir)
        self.agent_dir = directions[(idx + 1) % 4]
        self.score -= 1

    def shoot_arrow(self):
        if not self.has_arrow:
            return False

        self.has_arrow = False
        x, y = self.agent_pos
        hit = False

        if self.agent_dir == "up":
            for i in range(x - 1, self.grid_size):
                if self.world[i][y]["wumpus"]:
                    hit = True
                    self.world[i][y]["wumpus"] = False  # Wumpus is killed
                    break
        elif self.agent_dir == "down":
            for i in range(x + 1, -1, -1):
                if self.world[i][y]["wumpus"]:
                    self.world[i][y]["wumpus"] = False
                    hit = True
                    break
        elif self.agent_dir == "left":
            for j in range(y - 1, -1, -1):
                if self.world[x][j]["wumpus"]:
                    self.world[x][j]["wumpus"] = False
                    hit = True
                    break
        elif self.agent_dir == "right":
            for j in range(y + 1, self.grid_size):
                if self.world[x][j]["wumpus"]:
                    self.world[x][j]["wumpus"] = False
                    hit = True
                    break

        if hit:
            self.wumpus_alive = False
            self.percepts = self._update_percepts()
            self.percepts["scream"] = True
            self.score -= 10
            return True

        return False

    def grab_gold(self):
        x, y = self.agent_pos
        if self.world[x][y]["gold"]:
            self.has_gold = True
            self.world[x][y]["gold"] = False
            self.percepts["glitter"] = False
            self.score += 10
            return True
        return False

    def climb_out(self):
        if self.agent_pos != (0, 0):
            return False
        if not self.has_gold:
            self.game_over_state = "lose"
            self.score -= 1000
            return True
        self.game_over_state = "win"
        self.score += 1000
        return True

    def is_game_over(self, agent):
        if self.game_over_state is not None:
            return self.game_over_state

        x, y = self.agent_pos
        cell = self.world[x][y]

        # Kiểm tra nếu agent rơi vào pit hoặc bị wumpus ăn
        if cell["pit"] or (cell["wumpus"]):
            self.game_over_state = "lose"
            return "lose"

        # Kiêm tra nếu agent đã lấy vàng và trở về (0, 0)
        if self.agent_pos == (0, 0) and self.has_gold and agent.last_action == "climb":
            self.game_over_state = "win"
            return "win"
        if self.agent_pos == (0, 0) and not self.has_gold and agent.last_action == "climb":
            self.game_over_state = "lose"
            return "lose"
        return "continue"

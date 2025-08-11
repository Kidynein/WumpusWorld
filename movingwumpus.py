from typing import Tuple, List, Dict
from random import randint, choice, random
from environment import WumpusWorld
class MovingWumpusModule:
    def __init__(self, world: WumpusWorld):
        self.world = world

    def move_all_wumpus(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Move all Wumpus in the world to a random adjacent cell.
        Each Wumpus can move to any valid adjacent cell that is not occupied by another Wumpus or a pit.
        """
        moved_wumpus = []

        wumpus_positions = [(i, j) for i in range(self.world.grid_size)
                        for j in range(self.world.grid_size)
                        if self.world.world[i][j]["wumpus"]]

        for wx, wy in wumpus_positions:
            new_positions = [(wx + dx, wy + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            new_positions = [(nx, ny) for nx, ny in new_positions
                         if 0 <= nx < self.world.grid_size and 0 <= ny < self.world.grid_size
                         and not self.world.world[nx][ny]["pit"]
                         and not self.world.world[nx][ny]["wumpus"]]

            if new_positions:
                new_x, new_y = choice(new_positions)
                self.world.world[wx][wy]["wumpus"] = False
                self.world.world[new_x][new_y]["wumpus"] = True
                moved_wumpus.append(((wx, wy), (new_x, new_y)))
            else:
                moved_wumpus.append(((wx, wy), (wx, wy)))  

        return moved_wumpus


    def update(self, world, ui, agent):
        moved = self.move_all_wumpus()
        world.percepts = world._update_percepts()

        ui._update(world, agent)   
        ui.render()               

        if hasattr(agent, "_update_knowledge"):
            agent.update_knowledge(world.agent_pos, world.percepts, world)
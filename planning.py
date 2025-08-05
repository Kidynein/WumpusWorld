import random
import heapq
from typing import Set, Tuple, List

class Planning:
    def __init__(self, logic_inference):
        self.logic_inference = logic_inference
        self.world_size = logic_inference.world_size
        self.current_plan: List[str] = []

    def plan_next_action(self, current_pos: Tuple[int, int], current_dir: str, world) -> str:
        """
        Decide the next action based on current perceptions and KB:
        1. If there's glitter, grab gold.
        2. If holding gold, plan path back to (0,0).
        3. Otherwise, explore unvisited safe cells using A*.
        4. If a Wumpus location is known and arrow available, try shooting or move into shooting position.
        5. Take a risky move toward the nearest warning cell only if there are no safe moves
           OR with small probability epsilon < 0.05.
        6. If nothing else, wait.
        """
        self.current_plan.clear()

        if world.percepts.get("glitter", False):
            return "grab"

        if world.has_gold:
            path_home = self.find_path(current_pos, (0, 0), world)
            if path_home:
                self.current_plan = self._path_to_actions(path_home, current_dir)
                if self.current_plan:
                    return self.current_plan.pop(0)

        safe_unvisited = [cell for cell in self.logic_inference.safe_cells if cell not in self.logic_inference.visited_cells]
        if safe_unvisited:
            target = min(
                safe_unvisited,
                key=lambda c: abs(c[0] - current_pos[0]) + abs(c[1] - current_pos[1]),
            )
            path_to_target = self.find_path(current_pos, target, world)
            if path_to_target:
                self.current_plan = self._path_to_actions(path_to_target, current_dir)
                if self.current_plan:
                    return self.current_plan.pop(0)

        if world.has_arrow and self.logic_inference.wumpus_cells:
            wumpus_pos = next(iter(self.logic_inference.wumpus_cells))
            if self._can_shoot_wumpus(current_pos, current_dir, wumpus_pos):
                return "shoot"
            for shoot_pos in self._get_shooting_positions(wumpus_pos):
                if shoot_pos in self.logic_inference.safe_cells:
                    path_for_shoot = self.find_path(current_pos, shoot_pos, world)
                    if path_for_shoot:
                        self.current_plan = self._path_to_actions(path_for_shoot, current_dir)
                        if self.current_plan:
                            return self.current_plan.pop(0)

        epsilon = random.random()
        if self.logic_inference.warning_cells and (not safe_unvisited or epsilon < 0.05):
            target = min(
                self.logic_inference.warning_cells,
                key=lambda c: abs(c[0] - current_pos[0]) + abs(c[1] - current_pos[1]),
            )
            risky_path = self.find_risky_path(current_pos, target, world)
            if risky_path:
                self.current_plan = self._path_to_actions(risky_path, current_dir)
                if self.current_plan:
                    self.logic_inference.knowledge_base.append(f"Taking risky path to: {target} (ε={epsilon:.3f})")
                    return self.current_plan.pop(0)

        return "wait"

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        world,
    ) -> List[Tuple[int, int]] | None:
        """
        A* pathfinding (Manhattan distance) that strictly avoids confirmed unsafe cells.
        Returns a list of coordinates from start to goal, or None if no path exists.
        """
        if start == goal:
            return [start]

        def heuristic(cell: Tuple[int, int]) -> int:
            return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

        open_set = [(heuristic(start), 0, start, [start])]
        closed_set: Set[Tuple[int, int]] = set()

        while open_set:
            _, cost_so_far, current, path = heapq.heappop(open_set)
            if current in closed_set:
                continue
            closed_set.add(current)

            if current == goal:
                return path

            for nbr in world.get_neighbors(current):
                if nbr in closed_set or nbr in self.logic_inference.unsafe_cells:
                    continue
                new_cost = cost_so_far + 1
                new_path = path + [nbr]
                priority = new_cost + heuristic(nbr)
                heapq.heappush(open_set, (priority, new_cost, nbr, new_path))

        return None

    def find_risky_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        world,
    ) -> List[Tuple[int, int]] | None:
        """
        A* pathfinding that allows traveling through warning cells but still avoids confirmed unsafe cells.
        """
        if start == goal:
            return [start]

        def heuristic(cell: Tuple[int, int]) -> int:
            return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

        open_set = [(heuristic(start), 0, start, [start])]
        closed_set: Set[Tuple[int, int]] = set()

        while open_set:
            _, cost_so_far, current, path = heapq.heappop(open_set)
            if current in closed_set:
                continue
            closed_set.add(current)

            if current == goal:
                return path

            for nbr in world.get_neighbors(current):
                if nbr in closed_set or nbr in self.logic_inference.unsafe_cells:
                    continue
                new_cost = cost_so_far + 1
                new_path = path + [nbr]
                priority = new_cost + heuristic(nbr)
                heapq.heappush(open_set, (priority, new_cost, nbr, new_path))

        return None

    def _path_to_actions(
        self, path: List[Tuple[int, int]], current_dir: str
    ) -> List[str]:
        """
        Convert a (possibly non‐unique) list of next‐step coordinates into a sequence of moves.
        If 'path' contains more than one candidate next cell, pick one at random and generate
        the turns/move needed to enter it. (Ignores any further cells beyond the chosen one.)
        """
        if not path:
            return []

        next_cell = random.choice(path)
        cx, cy = path[0]
        nx, ny = next_cell

        if nx == cx + 1 and ny == cy:
            required = "up"
        elif nx == cx - 1 and ny == cy:
            required = "down"
        elif nx == cx and ny == cy - 1:
            required = "left"
        elif nx == cx and ny == cy + 1:
            required = "right"
        else:
            return []

        actions: List[str] = []
        direction = current_dir
        dir_order = ["up", "right", "down", "left"]

        while direction != required:
            actions.append("turn_left")
            direction = dir_order[(dir_order.index(direction) + 1) % 4]

        actions.append("move_forward")
        return actions

    def _can_shoot_wumpus(
        self,
        agent_pos: Tuple[int, int],
        agent_dir: str,
        wumpus_pos: Tuple[int, int],
    ) -> bool:
        """
        Check if the agent is aligned with Wumpus in the current facing direction.
        """
        ax, ay = agent_pos
        wx, wy = wumpus_pos

        if agent_dir == "up" and ay == wy and ax > wx:
            return True
        if agent_dir == "down" and ay == wy and ax < wx:
            return True
        if agent_dir == "left" and ax == wx and ay > wy:
            return True
        if agent_dir == "right" and ax == wx and ay < wy:
            return True

        return False

    def _get_shooting_positions(self, wumpus_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Return all cells in the same row or column as the Wumpus (excluding Wumpus's own cell).
        """
        wx, wy = wumpus_pos
        positions: List[Tuple[int, int]] = []

        for x in range(self.world_size):
            if x != wx:
                positions.append((x, wy))
        for y in range(self.world_size):
            if y != wy:
                positions.append((wx, y))

        return positions
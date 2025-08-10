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
        5. Take a risky move toward the nearest warning cell only if there are no safe moves.
        6. If nothing else, wait.
        """
        self.current_plan.clear()
        # 1. Grab gold if glitter
        if world.percepts.get("glitter", False):
            return "grab"

        # 2. Plan to go home if has gold
        if world.has_gold:
            if current_pos == (0, 0):
                return "climb"
            if not self.current_plan:
                path_home = self.find_path(current_pos, (0, 0), world, strict_safe=True)
                if path_home:
                    self.current_plan = self._path_to_actions(path_home, current_dir)
            if self.current_plan:
                return self.current_plan.pop(0)
            else:
                return "wait"

        # 3. Explore unvisited safe cells
        safe_unvisited = [cell for cell in self.logic_inference.safe_cells if cell not in self.logic_inference.visited_cells]
        if safe_unvisited:
            for target in safe_unvisited:
                path = self.find_path(current_pos, target, world, strict_safe=True)
                if path:
                    self.current_plan = self._path_to_actions(path, current_dir)
                    if self.current_plan:
                        return self.current_plan.pop(0)

        # 4. Try to shoot known Wumpus
        if world.has_arrow and self.logic_inference.wumpus_cells:
            wumpus_pos = next(iter(self.logic_inference.wumpus_cells))
            if self._can_shoot_wumpus(current_pos, current_dir, wumpus_pos):
                return "shoot"
            # Nếu cùng hàng hoặc cùng cột nhưng chưa đúng hướng -> xoay
            cx, cy = current_pos
            wx, wy = wumpus_pos

            if cx == wx:
                if cy < wy and current_dir != "right":
                    return "turn_right" if current_dir == "up" else "turn_left"
                elif cy > wy and current_dir != "left":
                    return "turn_left" if current_dir == "up" else "turn_right"
            elif cy == wy:
                if cx > wx and current_dir != "down":
                    return "turn_left" if current_dir == "left" else "turn_right"
                elif cx < wx and current_dir != "up":
                    return "turn_right" if current_dir == "left" else "turn_left"
            for shoot_pos in self._get_shooting_positions(wumpus_pos):
                if shoot_pos in self.logic_inference.safe_cells:
                    path = self.find_path(current_pos, shoot_pos, world, strict_safe=True)
                    if path:
                        self.current_plan = self._path_to_actions(path, current_dir)
                        if self.current_plan:
                            return self.current_plan.pop(0)
        
        # 5. Risky move to warning cell
        if self.logic_inference.warning_cells and not safe_unvisited:
            for target in self.logic_inference.warning_cells:
                path = self.find_risky_path(current_pos, target, world)
                if path:
                    self.current_plan = self._path_to_actions(path, current_dir)
                    if self.current_plan:
                        return self.current_plan.pop(0)

        # 6. Nothing to do
        return "wait"

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        world,
        strict_safe: bool = False,
    ) -> List[Tuple[int, int]] | None:
        """
        A* pathfinding avoiding confirmed unsafe cells (and optionally avoiding non-safe).
        """
        if start == goal:
            return [start]

        def heuristic(cell: Tuple[int, int]) -> int:
            return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

        open_set = [(heuristic(start), 0, start)]
        came_from: dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score = {start: 0}
        closed_set: Set[Tuple[int, int]] = set()

        while open_set:
            _, cost_so_far, current = heapq.heappop(open_set)

            if current == goal:
                # reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]

            if current in closed_set:
                continue
            closed_set.add(current)

            for nbr in world.get_neighbors(current):
                if nbr in closed_set or nbr in self.logic_inference.unsafe_cells:
                    continue
                if strict_safe and nbr not in self.logic_inference.safe_cells:
                    continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(nbr, float("inf")):
                    came_from[nbr] = current
                    g_score[nbr] = tentative_g
                    f_score = tentative_g + heuristic(nbr)
                    heapq.heappush(open_set, (f_score, tentative_g, nbr))

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

    def _path_to_actions(self, path: List[Tuple[int, int]], current_dir: str) -> List[str]:
        actions = []
        dir_order = ["up", "right", "down", "left"]
        direction = current_dir

        for i in range(len(path) - 1):
            cx, cy = path[i]
            nx, ny = path[i + 1]

            if nx == cx + 1 and ny == cy:
                required = "up"
            elif nx == cx - 1 and ny == cy:
                required = "down"
            elif nx == cx and ny == cy - 1:
                required = "left"
            elif nx == cx and ny == cy + 1:
                required = "right"
            else:
                continue  # skip invalid move

            if direction != required:
                cur_idx = dir_order.index(direction)
                req_idx = dir_order.index(required)

                # tính chênh lệch theo chiều kim đồng hồ
                cw = (req_idx - cur_idx) % 4

                if cw == 1:  # quay phải 1 lần
                    actions.append("turn_right")
                elif cw == 3:  # quay trái 1 lần
                    actions.append("turn_left")
                elif cw == 2:
                    actions.append("turn_right")

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

        if agent_dir == "up" and ay == wy and ax < wx:
            return True
        if agent_dir == "down" and ay == wy and ax > wx:
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

from typing import Set, Tuple, List

class LogicInference:
    def __init__(self, world_size: int = 5):
        self.world_size = world_size
        self.safe_cells: Set[Tuple[int, int]] = {(0, 0)}
        self.visited_cells: Set[Tuple[int, int]] = {(0, 0)}
        self.unsafe_cells: Set[Tuple[int, int]] = set()
        self.warning_cells: Set[Tuple[int, int]] = set()
        self.pit_cells: Set[Tuple[int, int]] = set()
        self.wumpus_cells: Set[Tuple[int, int]] = set()
        self.breeze_cells: Set[Tuple[int, int]] = set()
        self.stench_cells: Set[Tuple[int, int]] = set()
        self.knowledge_base: List[str] = ["Safe: (0,0)", "Visited: (0,0)"]

    def update_knowledge(self, pos: Tuple[int, int], percepts: dict, world) -> None:
        """
        Incorporate the current percepts at `pos` into the KB:
        - Mark visited cell as safe.
        - If there is a breeze or stench, note it and flag neighbors as warnings.
        - If there is neither breeze nor stench, mark all neighbors as safe.
        - When exactly one neighbor remains unvisited under a breeze/stench, deduce the pit/Wumpus.
        - Perform advanced deduction for pits if possible.
        """
        x, y = pos
        self.visited_cells.add(pos)
        self.safe_cells.add(pos)
        self.warning_cells.discard(pos)

        if pos != (0, 0):
            self.knowledge_base.append(f"Safe: {pos}")
            self.knowledge_base.append(f"Visited: {pos}")

        neighbors = world.get_neighbors(pos)

        if percepts.get("breeze", False):
            self.breeze_cells.add(pos)
            self.knowledge_base.append(f"Breeze at: {pos}")
            for nbr in neighbors:
                if nbr not in self.visited_cells and nbr not in self.safe_cells:
                    self.warning_cells.add(nbr)

        if percepts.get("stench", False):
            self.stench_cells.add(pos)
            self.knowledge_base.append(f"Stench at: {pos}")
            for nbr in neighbors:
                if nbr not in self.visited_cells and nbr not in self.safe_cells:
                    self.warning_cells.add(nbr)

        if not percepts.get("breeze", False) and not percepts.get("stench", False):
            for nbr in neighbors:
                if nbr not in self.safe_cells:
                    self.safe_cells.add(nbr)
                    self.warning_cells.discard(nbr)
                    self.knowledge_base.append(f"Deduced safe: {nbr}")

        if percepts.get("breeze", False):
            unvisited = [n for n in neighbors if n not in self.visited_cells]
            if len(unvisited) == 1:
                pit_pos = unvisited[0]
                self.pit_cells.add(pit_pos)
                self.unsafe_cells.add(pit_pos)
                self.warning_cells.discard(pit_pos)
                self.knowledge_base.append(f"Deduced pit at: {pit_pos}")

        if percepts.get("stench", False):
            unvisited = [n for n in neighbors if n not in self.visited_cells]
            if len(unvisited) == 1:
                wumpus_pos = unvisited[0]
                self.wumpus_cells.add(wumpus_pos)
                self.unsafe_cells.add(wumpus_pos)
                self.warning_cells.discard(wumpus_pos)
                self.knowledge_base.append(f"Deduced Wumpus at: {wumpus_pos}")

        self._advanced_deduction(world)

    def _advanced_deduction(self, world) -> None:
        """
        For each cell with a breeze, if all adjacent cells except one are known safe or pits,
        deduce that the remaining unknown cell must be a pit.
        """
        for breeze_pos in self.breeze_cells:
            neighbors = world.get_neighbors(breeze_pos)
            unknown = [
                n
                for n in neighbors
                if n not in self.visited_cells and n not in self.pit_cells
            ]
            known_pits = [n for n in neighbors if n in self.pit_cells]

            if len(unknown) == 1 and not known_pits:
                pit_pos = unknown[0]
                self.pit_cells.add(pit_pos)
                self.unsafe_cells.add(pit_pos)
                self.knowledge_base.append(f"Advanced deduction - pit at: {pit_pos}")
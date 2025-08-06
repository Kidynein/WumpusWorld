from typing import Set, Tuple, List

class LogicInference:
    def __init__(self, world_size: int = 8):
        self.world_size = world_size
        self.safe_cells: Set[Tuple[int, int]] = {(0, 0)}
        self.visited_cells: Set[Tuple[int, int]] = {(0, 0)}
        self.unsafe_cells: Set[Tuple[int, int]] = set()
        self.warning_cells: Set[Tuple[int, int]] = set()
        self.pit_cells: Set[Tuple[int, int]] = set()
        self.wumpus_cells: Set[Tuple[int, int]] = set()
        self.breeze_cells: Set[Tuple[int, int]] = set()
        self.stench_cells: Set[Tuple[int, int]] = set()
        self.knowledge_base: List[str] = ["Initial state: (0, 0) is Safe and Visited"]

        self.inference_rules = [
            self.rule_infer_pit_from_breeze,
            self.rule_infer_wumpus_from_stench,
            #self.rule_infer_safe_from_confirmed_pit
        ]

    def _add_knowledge(self, message: str):
        if message not in self.knowledge_base:
            self.knowledge_base.append(message)

    def update_knowledge(self, pos: Tuple[int, int], percepts: dict, world) -> None:
        self.visited_cells.add(pos)
        if pos not in self.safe_cells:
            self.safe_cells.add(pos)
            self._add_knowledge(f"Visited and confirmed Safe: {pos}")
        self.warning_cells.discard(pos)

        neighbors = world.get_neighbors(pos)

        has_breeze = percepts.get("breeze", False)
        has_stench = percepts.get("stench", False)
        has_scream = percepts.get("scream", False)
        if has_scream:
            wumpus_pos = self.wumpus_cells.pop() if self.wumpus_cells else None
            if wumpus_pos:
                self.safe_cells.add(wumpus_pos)
                self.unsafe_cells.discard(wumpus_pos)
                self._add_knowledge(f"Wumpus killed at {wumpus_pos}")

                wumpus_neighbors = world.get_neighbors(wumpus_pos)
                for nbr in wumpus_neighbors:
                    # Loại bỏ stench nếu có
                    if nbr in self.stench_cells:
                        self.stench_cells.discard(nbr)
                        self._add_knowledge(f"Stench at {nbr} removed after Wumpus killed")
            percepts["scream"] = False  # Reset scream after processing
                

                    
        if has_breeze:
            if pos not in self.breeze_cells:
                self.breeze_cells.add(pos)
                self._add_knowledge(f"Percept: Breeze at {pos}")
        if has_stench:
            if pos not in self.stench_cells:
                self.stench_cells.add(pos)
                self._add_knowledge(f"Percept: Stench at {pos}")

        if not has_breeze and not has_stench:
            for nbr in neighbors:
                if nbr not in self.safe_cells:
                    self.safe_cells.add(nbr)
                    self.warning_cells.discard(nbr)
                    self._add_knowledge(f"{pos} -> {nbr} is Safe")
        else:
            for nbr in neighbors:
                if (
                    nbr not in self.safe_cells
                    and nbr not in self.unsafe_cells
                    and nbr not in self.visited_cells
                ):
                    self.warning_cells.add(nbr)
                    self._add_knowledge(f"{pos} -> {nbr} is warning")

        self.forward_chaining(world)

    def forward_chaining(self, world) -> None:
        while True:
            change = False

            for rule in self.inference_rules:
                result = rule(world)

                for pit in result.get("pit", set()):
                    if pit not in self.pit_cells:
                        self.pit_cells.add(pit)
                        self.unsafe_cells.add(pit)
                        self.warning_cells.discard(pit)
                        self._add_knowledge(f"Pit at {pit}")
                        change = True

                for wumpus in result.get("wumpus", set()):
                    if wumpus not in self.wumpus_cells:
                        self.wumpus_cells.add(wumpus)
                        self.unsafe_cells.add(wumpus)
                        self.warning_cells.discard(wumpus)
                        self._add_knowledge(f"Wumpus at {wumpus}")
                        change = True

                for safe in result.get("safe", set()):
                    if safe not in self.safe_cells:
                        self.safe_cells.add(safe)
                        self.warning_cells.discard(safe)
                        self._add_knowledge(f"{safe} is Safe")
                        change = True

            if not change:
                break

    # ------------------------
    # RULE DEFINITIONS BELOW
    # ------------------------

    def rule_infer_pit_from_breeze(self, world):
        # Logic suy luận hố (pit)
        inferred = set()
        for breeze_pos in self.breeze_cells:
            neighbors = world.get_neighbors(breeze_pos)
            possible = [n for n in neighbors if n not in self.safe_cells]
            # Nếu chỉ còn một ô khả nghi duy nhất, nó phải là hố
            if len(possible) == 1:
                inferred.add(possible[0])
        return {"pit": inferred}

    def rule_infer_wumpus_from_stench(self, world):
        # Logic suy luận Wumpus
        inferred = set()
        for stench_pos in self.stench_cells:
            neighbors = world.get_neighbors(stench_pos)
            possible = [n for n in neighbors if n not in self.safe_cells]
            # Nếu chỉ còn một ô khả nghi duy nhất, nó phải là Wumpus
            if len(possible) == 1:
                inferred.add(possible[0])
        return {"wumpus": inferred}

    def rule_infer_safe_from_confirmed_pit(self, world):
        # Logic suy luận ô an toàn
            # Nếu một ô "warning" là hàng xóm của một ô "breeze",
            # nhưng tất cả các hàng xóm khác của ô "breeze" đó đều an toàn,
            # thì ô "warning" đó phải là hố.
            # Ngược lại, nếu ta tìm ra 1 hố cạnh ô breeze, các ô warning còn lại sẽ an toàn.
        inferred = set()
        for breeze_pos in self.breeze_cells:
            neighbors = world.get_neighbors(breeze_pos)
            pits = [n for n in neighbors if n in self.pit_cells]
            # Nếu đã tìm thấy hố gây ra breeze, các hàng xóm chưa an toàn còn lại là an toàn
            if pits:
                for n in neighbors:
                    if n not in self.safe_cells and n not in self.pit_cells:
                        inferred.add(n)
        return {"safe": inferred}
    # ------------------------
    # DEBUGGING
    # ------------------------

    def print_knowledge_base(self):
        print("\n".join(self.knowledge_base))

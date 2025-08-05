from inference import LogicInference
from planning import Planning
from typing import Tuple, List, Dict

class HybridAgent:
    def __init__(self, world_size: int = 5):
        """
        Initialize the HybridAgent, combining LogicInference and Planning modules.
        
        Args:
            world_size (int): Size of the game world grid (default is 8).
        """
        self.logic_inference = LogicInference(world_size)
        self.planning = Planning(self.logic_inference)
        self.world_size = world_size

    def update_knowledge(self, pos: Tuple[int, int], percepts: Dict, world) -> None:
        """
        Update the agent's knowledge base with new percepts at the given position.
        
        Args:
            pos (Tuple[int, int]): Current position of the agent.
            percepts (Dict): Dictionary of percepts (stench, breeze, glitter, etc.).
            world: The game world object providing neighbor information.
        """
        self.logic_inference.update_knowledge(pos, percepts, world)

    def plan_next_action(self, current_pos: Tuple[int, int], current_dir: str, world) -> str:
        """
        Plan the next action based on the current position, direction, and world state.
        
        Args:
            current_pos (Tuple[int, int]): Current position of the agent.
            current_dir (str): Current facing direction of the agent.
            world: The game world object providing game state and percepts.
            
        Returns:
            str: The next action to take ("move_forward", "turn_left", "turn_right", "grab", "shoot", or "wait").
        """
        return self.planning.plan_next_action(current_pos, current_dir, world)

    # Expose necessary attributes from LogicInference for UI or other components
    @property
    def safe_cells(self) -> set:
        return self.logic_inference.safe_cells

    @property
    def visited_cells(self) -> set:
        return self.logic_inference.visited_cells

    @property
    def unsafe_cells(self) -> set:
        return self.logic_inference.unsafe_cells

    @property
    def warning_cells(self) -> set:
        return self.logic_inference.warning_cells

    @property
    def pit_cells(self) -> set:
        return self.logic_inference.pit_cells

    @property
    def wumpus_cells(self) -> set:
        return self.logic_inference.wumpus_cells

    @property
    def breeze_cells(self) -> set:
        return self.logic_inference.breeze_cells

    @property
    def stench_cells(self) -> set:
        return self.logic_inference.stench_cells

    @property
    def knowledge_base(self) -> List[str]:
        return self.logic_inference.knowledge_base

    @property
    def current_plan(self) -> List[str]:
        return self.planning.current_plan
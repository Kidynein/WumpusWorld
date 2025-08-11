from inference import LogicInference
from planning import Planning
from typing import Tuple, List, Dict, Set
import random

class HybridAgent:
    def __init__(self, world_size: int = 8):
        """
        Khởi tạo HybridAgent, kết hợp các module LogicInference và Planning.

        Đối số:
            world_size(int): Kích thước của lưới thế giới trò chơi (mặc định là 8).
        """
        self.logic_inference = LogicInference(world_size)
        self.planning = Planning(self.logic_inference)
        self.last_action = ""

    def update_knowledge(self, pos: Tuple[int, int], percepts: Dict, world) -> None:
        """
        Cập nhật kiến thức của agent dựa trên vị trí hiện tại và các cảm nhận từ thế giới.
        Args:
            pos (Tuple[int, int]): Vị trí hiện tại của agent.
            percepts (Dict): Các cảm nhận từ thế giới (ví dụ: "stench", "breeze", "glitter").
            world: thê giới trò chơi cung cấp trạng thái và cảm nhận.
        """
        self.logic_inference.update_knowledge(pos, percepts, world)

    def plan_next_action(self, current_pos: Tuple[int, int], current_dir: str, world) -> str:
        """
        Lập kế hoạch hành động tiếp theo dựa trên vị trí hiện tại, hướng đi và trạng thái của thế giới.
        Args:
            current_pos (Tuple[int, int]): Vị trí hiện tại của agent.
            current_dir (str): Hướng hiện tại của agent ("up", "down", "left", "right").
            world: Thế giới trò chơi cung cấp trạng thái và cảm nhận.
        Trả về:
            str: Hành động tiếp theo của agent (ví dụ: "move_forward", "turn_left", "grab", "climb").
        """
        action = self.planning.plan_next_action(current_pos, current_dir, world)
        if action != "wait":
            self.last_action = action
        return action

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

class RandomAgent:
    def __init__(self):
        self._current_plan: List[str] = []
        self.last_action: str = ""
        # Phân phối hành động (tổng = 1). Có thể đặt đều 1/3 – 1/3 – 1/3
        self.action_probs = {
            "move_forward": 0.5,
            "turn_left":   0.2,
            "turn_right":  0.2,
            "shoot":    0.1,  # bắn ngẫu nhiên đôi lúc
        }

    def update_knowledge(self, pos: Tuple[int, int], percepts: Dict, world) -> None:
        pass  # không học gì, không suy luận

    def plan_next_action(self, current_pos: Tuple[int, int], current_dir: str, world) -> str:
        # 2 phản xạ tối thiểu
        if world.percepts.get("glitter", False):
            self.last_action = "grab"
            return "grab"
        if world.has_gold and current_pos == (0, 0):
            self.last_action = "climb"
            return "climb"

        # Lấy hành động ngẫu nhiên theo xác suất đã cấu hình
        items = list(self.action_probs.items())
        # Nếu không còn tên thì bỏ "shoot"
        if "shoot" in self.action_probs and not world.has_arrow:
            items = [(a,p) for a,p in items if a!="shoot"]

        s = sum(p for _, p in items) or 1.0
        actions, probs = zip(*[(a, p/s) for a,p in items])
        action = random.choices(actions, weights=probs, k=1)[0]
        self.last_action = action
        return action

    # Các thuộc tính cho GUI khỏi lỗi khi render
    @property
    def current_plan(self) -> List[str]: return self._current_plan
    @property
    def safe_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def visited_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def unsafe_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def warning_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def pit_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def wumpus_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def breeze_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def stench_cells(self) -> Set[Tuple[int,int]]: return set()
    @property
    def knowledge_base(self) -> List[str]: return ["Random baseline: no inference"]

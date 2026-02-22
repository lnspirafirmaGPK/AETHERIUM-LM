from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import math

class AgentRole(Enum):
    ORCHESTRATOR = "AgioSage"
    EVOLUTION = "Pangenes"
    VERIFIER = "PRM"
    TOOL = "Executor"

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    topic: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

@dataclass
class ThoughtNode:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    language: str = "th"  # "en" for logical pivot, "th" for context
    is_hidden: bool = True
    parent_id: Optional[str] = None
    children: List['ThoughtNode'] = field(default_factory=list)

    # MCTS metrics
    visit_count: int = 0
    total_reward: float = 0.0
    prm_score: float = 0.0  # Step-level reward from PRM

    def get_value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.total_reward / self.visit_count

    def ucb1(self, total_parent_visits: int, exploration_weight: float = 1.414) -> float:
        if self.visit_count == 0:
            return float('inf')
        exploitation = self.get_value()
        exploration = exploration_weight * math.sqrt(math.log(total_parent_visits) / self.visit_count)
        return exploitation + exploration

@dataclass
class ReasoningState:
    query: str = ""
    language_context: str = "th"
    history: List[Message] = field(default_factory=list)
    thought_root: Optional[ThoughtNode] = None
    current_node: Optional[ThoughtNode] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_complete: bool = False
    final_answer: Optional[str] = None

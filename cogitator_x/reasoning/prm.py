from typing import List
from ..core.models import ThoughtNode

class ProcessRewardModel:
    """
    The 'Conscience' of Cogitator-X. Evaluates each step of reasoning.
    In a real implementation, this would be a 7B/8B model trained as a classifier.
    """
    def __init__(self, model_name: str = "PRM-7B-Alpha"):
        self.model_name = model_name

    async def score_step(self, context_prompt: str, reasoning_path: List[str], current_step: str) -> float:
        """
        Calculates a score [0.0, 1.0] for the current step given the context.
        """
        # Logic Simulation for the demo:
        # 1. English logic pivot check: Give higher scores to steps that use logical connectors in English.
        # 2. Consistency check: Simulate a model's internal verification.

        score = 0.5 # Baseline

        # Heuristic: Logical connectors in English increase 'reasoning quality' signal
        logical_keywords = ["therefore", "because", "implies", "if", "then", "let", "assume", "step"]
        if any(kw in current_step.lower() for kw in logical_keywords):
            score += 0.2

        # Heuristic: Avoid loops
        if current_step in reasoning_path:
            score -= 0.4

        # Final clamping
        return max(0.0, min(1.0, score))

    async def evaluate_path(self, nodes: List[ThoughtNode]) -> float:
        """
        Aggregated score for a full reasoning path.
        """
        if not nodes:
            return 0.0
        scores = [node.prm_score for node in nodes]
        return sum(scores) / len(scores)

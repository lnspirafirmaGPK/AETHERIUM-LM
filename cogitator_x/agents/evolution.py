from typing import List, Dict, Any
from ..core.models import Message, AgentRole
from ..core.bus import AetherBus

class PangenesAgent:
    """
    The Evolution Agent of Cogitator-X.
    Implements the STaR (Self-Taught Reasoner) algorithm for recursive self-improvement.
    """
    def __init__(self, bus: AetherBus):
        self.bus = bus
        self.role = AgentRole.EVOLUTION.value
        self.wisdom_gems: List[Dict[str, Any]] = []

        # Subscribe to completion events to harvest high-quality data
        self.bus.subscribe("query.response", self.harvest_wisdom)

    async def harvest_wisdom(self, message: Message):
        """
        Phase 1: Filter & Rationalize.
        Collects successful reasoning traces to form 'Wisdom Gems'.
        """
        content = message.content
        answer = content.get("answer")
        trace = content.get("thought_trace")
        query = content.get("query")

        # In a real system, we check if answer == ground_truth
        # For this demo, we assume the PRM already validated it
        print(f"[{self.role}] Harvesting wisdom from successful trace. Trace length: {len(trace)}")

        gem = {
            "query": query,
            "reasoning_trace": trace,
            "final_answer": answer,
            "quality_score": 1.0 # Placeholder
        }

        self.wisdom_gems.append(gem)

        if len(self.wisdom_gems) >= 5:
            await self.trigger_evolution_cycle()

    async def trigger_evolution_cycle(self):
        """
        Phase 2: Fine-tune (Evolution).
        In a real system, this would trigger a GRPO/SFT training run.
        """
        print(f"[{self.role}] Evolving... Processing {len(self.wisdom_gems)} wisdom gems into the next model generation.")
        # Logic to trigger SFT/RL...
        self.wisdom_gems = [] # Reset after cycle

        evolution_msg = Message(
            sender=self.role,
            topic="system.evolution_complete",
            content={"generation": "N+1"}
        )
        await self.bus.publish(evolution_msg)

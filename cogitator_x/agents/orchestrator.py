import asyncio
from typing import Dict, Any, List
from ..core.models import Message, ReasoningState, AgentRole
from ..core.bus import AetherBus
from ..reasoning.mcts import MCTSReasoningEngine
from ..reasoning.prm import ProcessRewardModel

class AgioSageAgent:
    """
    The Orchestrator of Cogitator-X.
    Manages the reasoning loop and communicates via AetherBus.
    """
    def __init__(self, bus: AetherBus, engine: MCTSReasoningEngine):
        self.bus = bus
        self.engine = engine
        self.role = AgentRole.ORCHESTRATOR.value

        # Subscribe to query topics
        self.bus.subscribe("query.submit", self.handle_query)

    async def handle_query(self, message: Message):
        query = message.content.get("text", "")
        print(f"[{self.role}] Received query: {query}")

        state = ReasoningState(query=query)

        # 1. System 2 Reasoning Phase (Hidden CoT via MCTS)
        print(f"[{self.role}] Initiating System 2 reasoning (MCTS)...")
        best_path_nodes = await self.engine.run(state)

        # 2. Extract final thought and generate response
        thoughts = [node.text for node in best_path_nodes]
        state.metadata["thoughts"] = thoughts

        # 3. Simulate final output generation based on thoughts
        final_answer = self._generate_final_response(query, thoughts)
        state.final_answer = final_answer
        state.is_complete = True

        # 4. Publish response
        response_msg = Message(
            sender=self.role,
            topic="query.response",
            content={
                "answer": final_answer,
                "thought_trace": thoughts,
                "query": query
            }
        )
        await self.bus.publish(response_msg)

    def _generate_final_response(self, query: str, thoughts: List[str]) -> str:
        """
        In a real system, this would be another call to the LLM
        to synthesize the 'Hidden CoT' into a user-friendly answer.
        """
        # Logic simulation: Use the last thought as the base or synthesize
        if "ภาษาไทย" in query or "Thai" in query:
            return f"จากกระบวนการคิดที่ตรวจสอบแล้ว: {thoughts[-1]} (คำตอบสุดท้ายสำหรับคุณ)"
        return f"Final Answer based on reasoning: {thoughts[-1]}"

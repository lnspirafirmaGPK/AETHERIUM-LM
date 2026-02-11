import asyncio
import unittest
from cogitator_x.core.models import ReasoningState
from cogitator_x.reasoning.mcts import MCTSReasoningEngine
from cogitator_x.reasoning.prm import ProcessRewardModel

class TestMCTS(unittest.IsolatedAsyncioTestCase):
    async def test_mcts_flow(self):
        async def mock_gen(q, p):
            return ["Thought 1", "Thought 2"]

        prm = ProcessRewardModel()
        engine = MCTSReasoningEngine(prm=prm, generator=mock_gen, max_iterations=2)
        state = ReasoningState(query="Test Query")

        path = await engine.run(state)
        self.assertTrue(len(path) > 0)
        self.assertIn("Thought", path[0].text)

if __name__ == "__main__":
    unittest.main()

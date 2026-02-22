import asyncio
import unittest
from cogitator_x.core.models import ReasoningState, ThoughtNode
from cogitator_x.reasoning.mcts import MCTSReasoningEngine
from cogitator_x.reasoning.prm import ProcessRewardModel

class TestModels(unittest.TestCase):
    def test_thought_node_creation(self):
        node = ThoughtNode(text="Test thought")
        self.assertEqual(node.text, "Test thought")
        self.assertEqual(node.language, "th")
        self.assertEqual(node.visit_count, 0)

    def test_reasoning_state_creation(self):
        state = ReasoningState(query="Test Query")
        self.assertEqual(state.query, "Test Query")
        self.assertIsNone(state.thought_root)
        self.assertFalse(state.is_complete)

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

import random
import asyncio
import math
from typing import List, Optional, Callable
from ..core.models import ThoughtNode, ReasoningState
from .prm import ProcessRewardModel

class MCTSReasoningEngine:
    def __init__(self,
                 prm: ProcessRewardModel,
                 generator: Callable,
                 max_iterations: int = 10,
                 exploration_weight: float = 1.414):
        self.prm = prm
        self.generator = generator
        self.max_iterations = max_iterations
        self.exploration_weight = exploration_weight

    async def run(self, state: ReasoningState):
        if not state.thought_root:
            state.thought_root = ThoughtNode(text="Root", is_hidden=False)
            state.thought_root.visit_count = 1 # Prevent division by zero

        for i in range(self.max_iterations):
            # 1. Selection
            leaf = self._select(state.thought_root)

            # 2. Expansion
            new_nodes = await self._expand(leaf, state)

            # 3. Simulation & Evaluation
            for node in new_nodes:
                score = await self.prm.score_step(state.query, self._get_path_texts(node), node.text)
                node.prm_score = score
                # 4. Backpropagation
                self._backpropagate(node, score)

        # Select best path
        best_path = self._get_best_path(state.thought_root)
        return best_path

    def _select(self, node: ThoughtNode) -> ThoughtNode:
        while node.children:
            # Selection based on UCB1
            node = max(node.children, key=lambda n: n.ucb1(node.visit_count, self.exploration_weight))
        return node

    async def _expand(self, node: ThoughtNode, state: ReasoningState) -> List[ThoughtNode]:
        # Call the generator to get potential next thought steps
        # This simulates the "Adaptive Branching"
        path = self._get_path_texts(node)
        next_steps = await self.generator(state.query, path)

        new_nodes = []
        for step_text in next_steps:
            new_node = ThoughtNode(text=step_text, parent_id=node.id)
            new_node._parent_node = node # Link back for backprop
            node.children.append(new_node)
            new_nodes.append(new_node)
        return new_nodes

    def _backpropagate(self, node: ThoughtNode, reward: float):
        curr = node
        while curr:
            curr.visit_count += 1
            curr.total_reward += reward
            if hasattr(curr, '_parent_node'):
                curr = curr._parent_node
            else:
                break

    def _get_path_texts(self, node: ThoughtNode) -> List[str]:
        path = []
        curr = node
        while curr and curr.text != "Root":
            path.append(curr.text)
            if hasattr(curr, '_parent_node'):
                curr = curr._parent_node
            else:
                break
        return path[::-1]

    def _get_best_path(self, root: ThoughtNode) -> List[ThoughtNode]:
        path = []
        curr = root
        while curr.children:
            # Exploitation: select the most visited node
            curr = max(curr.children, key=lambda n: n.visit_count)
            path.append(curr)
        return path

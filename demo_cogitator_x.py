import asyncio
import random
from cogitator_x.core.models import Message
from cogitator_x.core.bus import AetherBus
from cogitator_x.reasoning.prm import ProcessRewardModel
from cogitator_x.reasoning.mcts import MCTSReasoningEngine
from cogitator_x.agents.orchestrator import AgioSageAgent
from cogitator_x.agents.evolution import PangenesAgent

async def mock_llm_generator(query, path):
    """
    Simulates a multilingual LLM generating reasoning steps.
    Uses English as logical pivot.
    """
    # Simple simulation logic
    if not path:
        return [
            "Let's break down the problem in Thai: 'หาผลรวมของ 15 และ 27'",
            "Analyze the request: Sum of 15 and 27."
        ]

    last_step = path[-1]
    if "Break down" in last_step or "Analyze" in last_step:
        return [
            "Step 1: Identify numbers: n1=15, n2=27.",
            "Step 1: Check the operation: addition required."
        ]

    if "Step 1" in last_step:
        return [
            "Step 2: Perform calculation: 15 + 27 = 42.",
            "Step 2: Calculation: 15 plus 27 equals 42."
        ]

    if "Step 2" in last_step:
        return [
            "Conclusion: The sum is 42. แปลเป็นไทยคือ 'ผลรวมคือ 42'"
        ]

    return ["Thinking..."]

async def main():
    print("=== Cogitator-X Architecture Demo ===")

    # Initialize components
    bus = AetherBus()
    prm = ProcessRewardModel()

    # Initialize MCTS Engine with mock generator
    engine = MCTSReasoningEngine(prm=prm, generator=mock_llm_generator, max_iterations=5)

    # Initialize Agents
    agio_sage = AgioSageAgent(bus, engine)
    pangenes = PangenesAgent(bus)

    # Subscribe to the final response to print it in this demo
    def on_response(msg):
        print(f"\n[USER OUTPUT] Question: {msg.content['query']}")
        print(f"[USER OUTPUT] Thought Trace:")
        for i, step in enumerate(msg.content['thought_trace']):
            print(f"  {i+1}. {step}")
        print(f"[USER OUTPUT] Final Answer: {msg.content['answer']}\n")

    bus.subscribe("query.response", on_response)

    # Submit a query
    query_msg = Message(
        topic="query.submit",
        content={"text": "ช่วยหาผลรวมของ 15 และ 27 หน่อย"}
    )

    print("\nSubmitting query...")
    await bus.publish(query_msg)

    # Wait for processing
    await asyncio.sleep(2)
    print("=== Demo Complete ===")

if __name__ == "__main__":
    asyncio.run(main())

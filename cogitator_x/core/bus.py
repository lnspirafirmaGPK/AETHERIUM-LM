import asyncio
import inspect
from typing import Callable, Dict, List, Any
from .models import Message

class AetherBus:
    """
    The Digital Nervous System (Messaging Substrate) for Cogitator-X.
    Uses a simple Pub/Sub pattern to connect AgioSage, Pangenes, and Tools.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def publish(self, message: Message):
        topic = message.topic
        if topic in self.subscribers:
            tasks = []
            for callback in self.subscribers[topic]:
                if inspect.iscoroutinefunction(callback):
                    tasks.append(callback(message))
                else:
                    # Run sync callback in a thread or just call it
                    callback(message)

            if tasks:
                await asyncio.gather(*tasks)

    async def request(self, topic: str, content: Dict[str, Any]) -> Message:
        response = Message(topic=f"{topic}.response", content={"status": "received"})
        return response

import asyncio
import inspect
import uuid
from typing import Callable, Dict, List, Any
from .models import Message

class AetherBus:
    """
    The Digital Nervous System (Messaging Substrate) for Cogitator-X.
    Uses a simple Pub/Sub pattern to connect AgioSage, Pangenes, and Tools.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.futures: Dict[str, asyncio.Future] = {}

    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def publish(self, message: Message):
        correlation_id = message.content.get('correlation_id')
        if correlation_id and correlation_id in self.futures:
            future = self.futures.pop(correlation_id)
            if not future.done():
                future.set_result(message)
            return

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

    async def request(self, topic: str, content: Dict[str, Any], timeout: float = 5.0) -> Message:
        correlation_id = str(uuid.uuid4())
        future = asyncio.Future()
        self.futures[correlation_id] = future

        request_message = Message(
            topic=topic,
            content={**content, 'correlation_id': correlation_id}
        )

        await self.publish(request_message)

        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.futures.pop(correlation_id, None)
            raise TimeoutError(f"Request to topic '{topic}' timed out.")

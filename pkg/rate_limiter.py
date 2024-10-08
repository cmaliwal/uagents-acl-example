import os
from datetime import datetime
from typing import Any, Callable
from pydantic import BaseModel
from uagents import Context
from uagents.models import ErrorMessage
from uagents.storage import StorageAPI

WINDOW_SIZE_MINUTES = int(os.getenv("WINDOW_SIZE_MINUTES", "60"))
MAX_REQUESTS = int(os.getenv("MAX_REQUESTS", "6"))


class Usage(BaseModel):
    time_window_start: float
    requests: int


class RateLimiter:
    """
    Rate limiter for API requests using agent's storage.
    """

    def __init__(self, storage: StorageAPI, window_size_minutes: int = WINDOW_SIZE_MINUTES, max_requests: int = MAX_REQUESTS):
        self.storage = storage
        self.window_size_minutes = window_size_minutes
        self.max_requests = max_requests

    def add_request(self, agent_address: str) -> bool:
        """
        Add a request to the rate limiter and check if the agent is within the allowed limit.
        """
        now = datetime.now().timestamp()

        if self.storage.has(agent_address):
            usage = Usage(**self.storage.get(agent_address))

            if (now - usage.time_window_start) <= self.window_size_minutes * 60:
                if usage.requests >= self.max_requests:
                    return False
                usage.requests += 1
            else:
                usage.time_window_start = now
                usage.requests = 1
        else:
            usage = Usage(time_window_start=now, requests=1)

        self.storage.set(agent_address, usage.model_dump())
        return True

    def wrap(self, func: Callable):
        """
        Decorator to wrap a function with rate limiting.
        """

        async def decorator(ctx: Context, sender: str, msg: Any):
            if self.add_request(sender):
                await func(ctx, sender, msg)
            else:
                ctx.logger.warning(f"Rate limit exceeded for agent {sender}.")
                await ctx.send(
                    sender,
                    ErrorMessage(error="Rate limit exceeded. Try again later."),
                )
            return

        return decorator

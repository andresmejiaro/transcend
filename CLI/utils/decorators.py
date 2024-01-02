# utils/decorators.py

import time
import asyncio
import functools

from utils.logger import log_message


def frame_rate_decorator(frame_rate):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            await asyncio.sleep(max(0, 1 / frame_rate - elapsed_time))
            return result
        return wrapper
    return decorator
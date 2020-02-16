from functools import wraps

from redis_ratelimit.exceptions import RateLimited
from redis_ratelimit.utils import is_rate_limited, default_pool


def ratelimit(rate, key, redis_pool: dict = default_pool):
    def decorator(func):
        @wraps(func)
        async def decorated_function(*args, **kwargs):
            if is_rate_limited(rate, key, func, redis_pool):
                raise RateLimited("Too Many Requests")
            return await func(*args, **kwargs)

        return decorated_function

    return decorator

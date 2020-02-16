import re
import redis

from redis_ratelimit.exceptions import RateLimiterException

default_pool = {"host": "localhost", "port": 6379, "db": 10}
rate_re = re.compile(r"([\d]+)/([\d]*)([smhd])")
UNITS = {"s": 1, "m": 60, "h": 60 * 60, "d": 24 * 60 * 60}


def parse_rate(rate: str):
    try:
        count, factor, unit = rate_re.match(rate).groups()
        count = int(count)
        seconds = UNITS[unit.lower()]
        if factor:
            seconds *= int(factor)
        return count, seconds
    except ValueError:
        raise RateLimiterException("Invalid rate value")


def is_rate_limited(rate: str, key: str, value: str, redis_pool: dict):
    if not rate:
        return (None, None)

    count, seconds = parse_rate(rate)
    redis_key = f"[{key}][{value}][{count}/{seconds}]"

    r = redis.Redis(**redis_pool)

    current = r.get(redis_key)
    if current:
        current = int(current.decode("utf-8"))
        if current >= count:
            return (True, (count - (current if current else 0), count))

    value = r.incr(redis_key)
    if value == 1:
        r.expire(redis_key, seconds)

    return (False, (count - (current if current else 0), count))

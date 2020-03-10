import re
import time
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


def calc_ttl(seconds: int):
    return int(time.time() + (seconds))

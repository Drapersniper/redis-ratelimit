import redis
from redis_ratelimit.utils import calc_ttl, default_pool, parse_rate


class RateLimit:
    def __init__(
        self, rate: str, key: str, value: str, redis_pool: dict = default_pool,
    ):
        self.rate = rate
        self.key = key
        self.value = value
        self.pool = redis_pool

    @property
    def check(self):
        return self.is_rate_limited()

    def is_rate_limited(self):
        if not self.rate:
            return (None, (None, None, None))

        count, seconds = parse_rate(self.rate)
        redis_key = f"[{self.key}][{self.value}][{count}/{seconds}]"

        r = redis.Redis(**self.pool)

        current = r.get(redis_key)
        if current:
            current = int(current.decode("utf-8"))
            if current >= count:
                return (
                    True,
                    (count, count - (current if current else 0), calc_ttl(r.ttl(redis_key))),
                )

        value = r.incr(redis_key)
        if value == 1:
            r.expire(redis_key, seconds)

        return (False, (count, count - (current if current else 0), calc_ttl(r.ttl(redis_key))))

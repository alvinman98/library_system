import redis
import json
from flask import current_app

def get_redis_client():
    return redis.Redis.from_url(current_app.config["REDIS_URL"])

def get_cache(key):
    r = get_redis_client()
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cache(key, value, ex=60):
    r = get_redis_client()
    r.set(key, json.dumps(value), ex=ex)  # ex: expired in 60 seconds

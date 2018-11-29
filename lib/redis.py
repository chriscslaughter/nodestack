import redis
from django.conf import settings

TTL_1_HOUR = 3600

redis_pool = None

def redis_factory(host, port, db, password):
    global redis_pool
    if not redis_pool:
        redis_pool = redis.ConnectionPool(host=host,
                                          port=port,
                                          db=db,
                                          decode_responses=True,
                                          password=password)
    return redis.StrictRedis(connection_pool=redis_pool)

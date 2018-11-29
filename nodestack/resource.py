from lib.redis import redis_factory
from django.conf import settings

def get_redis():
    return redis_factory(settings.REDIS_HOST,
                         settings.REDIS_PORT,
                         settings.REDIS_DB,
                         settings.REDIS_PASSWORD)

import redis
from rq import Queue

redis_connection = redis.Redis(host="db", port=6379)
task_queue = Queue(connection=redis_connection)

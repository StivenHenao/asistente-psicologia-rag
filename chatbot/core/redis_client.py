import redis

SESSION_DURATION = 60 * 60 * 24 * 2  # 2 dias

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def save_session(user_id):
    redis_client.set("auth_user_id", user_id, ex=SESSION_DURATION)

def get_session():
    return redis_client.get("auth_user_id")

def delete_session():
    redis_client.delete("auth_user_id")

def session_ttl():
    return redis_client.ttl("auth_user_id")

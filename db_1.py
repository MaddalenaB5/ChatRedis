import redis

redis = redis.Redis(host='localhost', port=18934, db=0, charset="utf-8", decode_responses=True)

print('connesso')
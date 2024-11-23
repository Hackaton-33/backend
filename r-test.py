import redis

#Подключение к БД
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.keys())
#print(r.get(b"2024-01-01 00:00:00"))

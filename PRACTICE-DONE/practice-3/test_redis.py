import redis
import json

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# CREATE
user = {"name": "Anna", "age": 25}
r.set("user:1", json.dumps(user))
print("Created:", user)

# READ
data = r.get("user:1")
user = json.loads(data)
print("Read:", user)

# UPDATE
user["age"] = 26
r.set("user:1", json.dumps(user))
print("Updated:", user)

# DELETE
r.delete("user:1")
print("Deleted user:1")

# LIST ALL
keys = r.keys("user:*")
print("All users:", keys)
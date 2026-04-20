from fastapi import FastAPI, HTTPException
import redis
import json


app = FastAPI()

# r = redis.Redis(host='redis-server', port=6379, decode_responses=True)
r = redis.Redis(host='localhost', port=6381, decode_responses=True)

@app.get("/")
def root():
    return {"message": "FastAPI + Redis CRUD API"}

@app.get("/health/redis")
def test_redis():
    try:
        r.ping()
        return {"status": "connected", "message": "Redis is working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/test")
def test_post(name: str, value: str):
    r.set(name, value)
    return {"status": "saved", "name": name, "value": value}


@app.get("/items/stats/count")
def count_items():
    count = len(r.keys("*"))
    return {"total_items": count}



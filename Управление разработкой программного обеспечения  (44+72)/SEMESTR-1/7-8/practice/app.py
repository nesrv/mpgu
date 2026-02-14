from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Item(BaseModel):
    name: str
    value: str

@app.get("/")
def root():
    return {"message": "FastAPI + Redis CRUD API"}

@app.post("/items/{item_id}")
def create_item(item_id: str, item: Item):
    r.set(item_id, json.dumps(item.dict()))
    return {"item_id": item_id, "status": "created"}

@app.get("/items/{item_id}")
def read_item(item_id: str):
    data = r.get(item_id)
    if not data:
        raise HTTPException(status_code=404, detail="Item not found")
    return json.loads(data)

@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    if not r.exists(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    r.set(item_id, json.dumps(item.dict()))
    return {"item_id": item_id, "status": "updated"}

@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    if not r.delete(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "status": "deleted"}

@app.get("/items")
def list_items():
    keys = r.keys("*")
    items = {}
    for key in keys:
        items[key] = json.loads(r.get(key))
    return items
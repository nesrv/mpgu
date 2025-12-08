from fastapi import FastAPI
import os
import time

app = FastAPI()

# Счетчик в памяти (для простоты)
counter = 0

@app.get("/")
def read_root():
    return {"message": "Docker Compose Lab", "service": "FastAPI"}

@app.post("/hit")
def hit():
    global counter
    counter += 1
    return {"count": counter}

@app.get("/debug")
def debug_info():
    return {
        "debug": os.getenv("DEBUG", "false"),
        "hostname": os.getenv("HOSTNAME", "unknown"),
        "counter": counter
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
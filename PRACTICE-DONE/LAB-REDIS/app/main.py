from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import Counter, SessionLocal, engine, Base
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.post("/hit")
async def hit(db: AsyncSession = Depends(get_db)):
    counter = await db.get(Counter, 1)
    if not counter:
        counter = Counter(id=1, value=0)
        db.add(counter)
    counter.value += 1
    await db.commit()
    return {"count": counter.value}

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
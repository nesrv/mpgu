from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    popularity: int = 0

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    popularity: int

    class Config:
        from_attributes = True

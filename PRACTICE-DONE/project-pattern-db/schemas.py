from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    data: dict = {}

class StudentResponse(BaseModel):
    id: int
    name: str
    data: dict
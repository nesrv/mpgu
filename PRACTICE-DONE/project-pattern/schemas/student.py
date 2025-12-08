from pydantic import BaseModel, Field
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    group: str
    year: int
    courses: list[int] = []

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)
    courses: Optional[list[int]] = None

class StudentResponse(BaseModel):
    name: str
    group: str
    year: int
    courses: list[int]
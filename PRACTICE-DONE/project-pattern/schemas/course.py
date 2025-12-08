from pydantic import BaseModel
from typing import Optional

class CourseCreate(BaseModel):
    id: int
    name: str
    credits: int
    semester: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[int] = None

class CourseResponse(BaseModel):
    id: int
    name: str
    credits: int
    semester: int
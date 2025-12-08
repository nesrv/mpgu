from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)
    courses: list[int] = []

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)
    courses: Optional[list[int]] = None

class Course(BaseModel):
    id: int
    name: str
    credits: int
    semester: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[int] = None
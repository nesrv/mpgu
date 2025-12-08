from pydantic import BaseModel, Field

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)
    courses: list[int] = []
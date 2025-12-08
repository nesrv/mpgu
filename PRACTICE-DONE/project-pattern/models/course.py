from pydantic import BaseModel

class Course(BaseModel):
    id: int
    name: str
    credits: int
    semester: int
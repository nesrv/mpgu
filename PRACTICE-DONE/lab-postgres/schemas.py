from pydantic import BaseModel, ConfigDict
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    email: str
    status: str = 'active'

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GradeResponse(BaseModel):
    student_id: int
    course_id: int
    grade: float
    
    model_config = ConfigDict(from_attributes=True)

class SQLQuery(BaseModel):
    query: str

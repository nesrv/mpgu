from models.student import Student
from schemas.student import StudentCreate, StudentUpdate
from repositories.student_repository import StudentRepository
from typing import List, Optional

class StudentService:
    def __init__(self):
        self.repository = StudentRepository()
    
    def load_fixture(self):
        return self.repository.load_fixture()
    
    def get_all(self, year: Optional[int] = None, group: Optional[str] = None) -> List[Student]:
        return self.repository.get_all(year, group)
    
    def search(self, query: str) -> List[Student]:
        return self.repository.search(query)
    
    def get_by_name(self, name: str) -> Optional[Student]:
        return self.repository.get_by_name(name)
    
    def create(self, student_data: StudentCreate) -> Student:
        student = Student(**student_data.model_dump())
        return self.repository.create(student)
    
    def update(self, name: str, student_data: StudentUpdate) -> Optional[Student]:
        return self.repository.update(name, student_data.model_dump(exclude_unset=True))
    
    def delete(self, name: str) -> bool:
        return self.repository.delete(name)
    
    def enroll(self, name: str, course_id: int) -> bool:
        return self.repository.enroll(name, course_id)
    
    def unenroll(self, name: str, course_id: int) -> bool:
        return self.repository.unenroll(name, course_id)
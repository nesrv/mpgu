from models.student import Student
from typing import List, Optional

class StudentRepository:
    def __init__(self):
        self._students: List[Student] = []
    
    def get_all(self) -> List[Student]:
        return self._students
    
    def get_by_name(self, name: str) -> Optional[Student]:
        return next((s for s in self._students if s.name == name), None)
    
    def create(self, student: Student) -> Student:
        self._students.append(student)
        return student
    
    def update(self, name: str, student: Student) -> Optional[Student]:
        for i, s in enumerate(self._students):
            if s.name == name:
                self._students[i] = student
                return student
        return None
    
    def delete(self, name: str) -> bool:
        for i, s in enumerate(self._students):
            if s.name == name:
                self._students.pop(i)
                return True
        return False
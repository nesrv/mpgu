from models.student import Student
from typing import Optional
import json

class StudentRepository:
    def __init__(self):
        self._students: list[Student] = []
    
    def load_fixture(self):
        with open("fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self._students = [Student(**item) for item in data]
    
    def get_all(self, year: Optional[int] = None, group: Optional[str] = None) -> list[Student]:
        result = self._students
        if year:
            result = [s for s in result if s.year == year]
        if group:
            result = [s for s in result if s.group == group]
        return result
    
    def search(self, query: str) -> list[Student]:
        return [s for s in self._students if query.lower() in s.name.lower()]
    
    def get_by_name(self, name: str) -> Optional[Student]:
        return next((s for s in self._students if s.name == name), None)
    
    def create(self, student: Student) -> Student:
        self._students.append(student)
        return student
    
    def update(self, name: str, data: dict) -> Optional[Student]:
        for i, s in enumerate(self._students):
            if s.name == name:
                updated = s.model_dump()
                updated.update(data)
                self._students[i] = Student(**updated)
                return self._students[i]
        return None
    
    def delete(self, name: str) -> bool:
        for i, s in enumerate(self._students):
            if s.name == name:
                self._students.pop(i)
                return True
        return False
    
    def enroll(self, name: str, course_id: int) -> bool:
        student = self.get_by_name(name)
        if student and course_id not in student.courses:
            student.courses.append(course_id)
            return True
        return False
    
    def unenroll(self, name: str, course_id: int) -> bool:
        student = self.get_by_name(name)
        if student and course_id in student.courses:
            student.courses.remove(course_id)
            return True
        return False
    
    def get_students_by_course(self, course_id: int) -> list[Student]:
        return [s for s in self._students if course_id in s.courses]
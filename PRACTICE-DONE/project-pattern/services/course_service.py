from models.course import Course
from repositories.course_repository import CourseRepository
from repositories.student_repository import StudentRepository
from typing import List, Optional

class CourseService:
    def __init__(self):
        self.course_repository = CourseRepository()
        self.student_repository = StudentRepository()
    
    def get_all(self) -> List[Course]:
        return self.course_repository.get_all()
    
    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.course_repository.get_by_id(course_id)
    
    def get_students_by_course(self, course_id: int):
        return self.student_repository.get_students_by_course(course_id)
from models.course import Course
from typing import Optional

class CourseRepository:
    def __init__(self):
        self._courses: list[Course] = [
            Course(id=1, name="Программирование", credits=4, semester=1),
            Course(id=2, name="Математика", credits=3, semester=1),
            Course(id=3, name="Базы данных", credits=3, semester=2)
        ]
    
    def get_all(self) -> list[Course]:
        return self._courses
    
    def get_by_id(self, course_id: int) -> Optional[Course]:
        return next((c for c in self._courses if c.id == course_id), None)
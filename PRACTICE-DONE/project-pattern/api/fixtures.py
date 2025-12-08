from fastapi import APIRouter
from services.student_service import StudentService
from services.course_service import CourseService
import json

router = APIRouter(prefix="/fixtures", tags=["fixtures"])

# Глобальные сервисы для доступа к репозиториям
student_service = StudentService()
course_service = CourseService()

@router.post("/load-all")
def load_all_fixtures():
    """Загрузить все тестовые данные (студенты и курсы)"""
    with open("fixtures_full.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Очистка существующих данных
    student_service.repository._students.clear()
    course_service.course_repository._courses.clear()
    
    # Загрузка студентов
    from models.student import Student
    student_service.repository._students = [Student(**item) for item in data["students"]]
    
    # Загрузка курсов
    from models.course import Course
    course_service.course_repository._courses = [Course(**item) for item in data["courses"]]
    
    return {
        "message": "All fixtures loaded successfully",
        "students_count": len(student_service.repository._students),
        "courses_count": len(course_service.course_repository._courses)
    }

@router.delete("/clear-all")
def clear_all_data():
    """Очистить все данные"""
    student_service.repository._students.clear()
    course_service.course_repository._courses.clear()
    
    return {"message": "All data cleared"}

@router.get("/status")
def get_status():
    """Получить статус загруженных данных"""
    return {
        "students_count": len(student_service.repository._students),
        "courses_count": len(course_service.course_repository._courses)
    }
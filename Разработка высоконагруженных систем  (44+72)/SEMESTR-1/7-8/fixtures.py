from fastapi import APIRouter
import json
import students
import courses

router = APIRouter(prefix="/fixtures", tags=["fixtures"])

@router.post("/load-all")
def load_all_fixtures():
    """Загрузить все тестовые данные (студенты и курсы)"""
    with open("fixtures_full.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Загрузка студентов
    students._students = [students.Student(**item) for item in data["students"]]
    
    # Загрузка курсов
    courses._courses = [courses.Course(**item) for item in data["courses"]]
    
    return {
        "message": "All fixtures loaded successfully",
        "students_count": len(students._students),
        "courses_count": len(courses._courses)
    }

@router.delete("/clear-all")
def clear_all_data():
    """Очистить все данные"""
    students._students.clear()
    courses._courses.clear()
    
    return {"message": "All data cleared"}

@router.get("/status")
def get_status():
    """Получить статус загруженных данных"""
    return {
        "students_count": len(students._students),
        "courses_count": len(courses._courses)
    }
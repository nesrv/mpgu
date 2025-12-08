from fastapi import APIRouter, HTTPException
from models import Course, CourseUpdate, Student
from typing import Optional
import students
import json

router = APIRouter(prefix="/courses", tags=["courses"])

# In-memory storage
_courses: list[Course] = []

@router.post("/load-fixture")
def load_fixture():
    global _courses
    with open("fixtures_full.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    _courses = [Course(**item) for item in data["courses"]]
    return {"message": f"Loaded {len(_courses)} courses"}

@router.get("/")
def get_all() -> list[Course]:
    return _courses

@router.get("/{course_id}")
def get_one(course_id: int) -> Course:
    course = next((c for c in _courses if c.id == course_id), None)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@router.post("/")
def create(course: Course) -> Course:
    _courses.append(course)
    return course

@router.patch("/{course_id}")
def update(course_id: int, data: CourseUpdate) -> Course:
    for i, c in enumerate(_courses):
        if c.id == course_id:
            updated = c.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _courses[i] = Course(**updated)
            return _courses[i]
    raise HTTPException(404, "Course not found")

@router.delete("/{course_id}")
def delete(course_id: int):
    for i, c in enumerate(_courses):
        if c.id == course_id:
            _courses.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(404, "Course not found")

@router.get("/{course_id}/students")
def get_students(course_id: int) -> list[Student]:
    return [s for s in students._students if course_id in s.courses]
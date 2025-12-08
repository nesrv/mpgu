from fastapi import APIRouter, HTTPException, Query
from models import Student, StudentUpdate
from typing import Optional
import json

router = APIRouter(prefix="/students", tags=["students"])

# In-memory storage
_students: list[Student] = []

@router.post("/load-fixture")
def load_fixture():
    global _students
    with open("fixtures_full.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    _students = [Student(**item) for item in data["students"]]
    return {"message": f"Loaded {len(_students)} students"}

@router.get("/")
def get_all(year: Optional[int] = None, group: Optional[str] = None) -> list[Student]:
    result = _students
    if year:
        result = [s for s in result if s.year == year]
    if group:
        result = [s for s in result if s.group == group]
    return result

@router.get("/search")
def search(query: str = Query(...)) -> list[Student]:
    return [s for s in _students if query.lower() in s.name.lower()]

@router.get("/{name}")
def get_one(name: str) -> Student:
    student = next((s for s in _students if s.name == name), None)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/")
def create(student: Student) -> Student:
    _students.append(student)
    return student

@router.patch("/{name}")
def update(name: str, data: StudentUpdate) -> Student:
    for i, s in enumerate(_students):
        if s.name == name:
            updated = s.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _students[i] = Student(**updated)
            return _students[i]
    raise HTTPException(404, "Student not found")

@router.delete("/{name}")
def delete(name: str):
    for i, s in enumerate(_students):
        if s.name == name:
            _students.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(404, "Student not found")

@router.post("/{name}/enroll/{course_id}")
def enroll(name: str, course_id: int):
    for student in _students:
        if student.name == name:
            if course_id not in student.courses:
                student.courses.append(course_id)
            return {"message": "Enrolled"}
    raise HTTPException(404, "Student not found")

@router.delete("/{name}/unenroll/{course_id}")
def unenroll(name: str, course_id: int):
    for student in _students:
        if student.name == name:
            if course_id in student.courses:
                student.courses.remove(course_id)
            return {"message": "Unenrolled"}
    raise HTTPException(404, "Student not found")
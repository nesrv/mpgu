from fastapi import APIRouter, HTTPException, Query
from schemas.student import StudentCreate, StudentUpdate, StudentResponse
from services.student_service import StudentService
from typing import List, Optional

router = APIRouter(prefix="/students", tags=["students"])
service = StudentService()

@router.post("/load-fixture")
def load_fixture():
    service.load_fixture()
    return {"message": "Loaded students from fixture"}

@router.get("/", response_model=List[StudentResponse])
def get_all(year: Optional[int] = None, group: Optional[str] = None):
    return service.get_all(year, group)

@router.get("/search", response_model=List[StudentResponse])
def search(query: str = Query(...)):
    return service.search(query)

@router.get("/{name}", response_model=StudentResponse)
def get_one(name: str):
    student = service.get_by_name(name)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/", response_model=StudentResponse)
def create(student: StudentCreate):
    return service.create(student)

@router.patch("/{name}", response_model=StudentResponse)
def update(name: str, data: StudentUpdate):
    student = service.update(name, data)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.delete("/{name}")
def delete(name: str):
    if not service.delete(name):
        raise HTTPException(404, "Student not found")
    return {"message": "Deleted"}

@router.post("/{name}/enroll/{course_id}")
def enroll(name: str, course_id: int):
    if not service.enroll(name, course_id):
        raise HTTPException(404, "Student not found")
    return {"message": "Enrolled"}

@router.delete("/{name}/unenroll/{course_id}")
def unenroll(name: str, course_id: int):
    if not service.unenroll(name, course_id):
        raise HTTPException(404, "Student not found")
    return {"message": "Unenrolled"}


from fastapi import APIRouter, HTTPException
from schemas.course import CourseResponse
from schemas.student import StudentResponse
from services.course_service import CourseService
from typing import List

router = APIRouter(prefix="/courses", tags=["courses"])
service = CourseService()

@router.get("/", response_model=List[CourseResponse])
def get_all_courses():
    return service.get_all()

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int):
    course = service.get_by_id(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@router.get("/{course_id}/students", response_model=List[StudentResponse])
def get_students_by_course(course_id: int):
    return service.get_students_by_course(course_id)
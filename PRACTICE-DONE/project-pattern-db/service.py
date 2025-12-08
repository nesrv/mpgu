from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models import StudentModel, CourseModel, Base, engine
from schemas import StudentResponse, StudentCreate
import json

class StudentService:
    def __init__(self, db):
        self.db = db
    
    def load_fixture(self):
        # Удаляем и создаем таблицы заново
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        with open("fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Загружаем студентов как есть (с ID из фикстур)
        for student_data in data["students"]:
            student = StudentModel(**student_data)
            self.db.add(student)
        
        # Загружаем курсы
        for course_data in data["courses"]:
            course_id = course_data["id"]
            course_name = course_data["name"]
            
            enrolled_students = [e["student_id"] for e in data["enrollments"] if e["course_id"] == course_id]
            
            for student_id in enrolled_students:
                course = CourseModel(name=course_name, student_id=student_id)
                self.db.add(course)
        
        self.db.commit()
        
        # Сбрасываем последовательность чтобы новые студенты получали правильные ID
       # Сбрасываем последовательность чтобы новые студенты получали правильные ID  
        max_id = self.db.query(func.max(StudentModel.id)).scalar() or 0
        self.db.execute(func.setval('students_id_seq', max_id))
    
    def get_all(self):
        students = self.db.query(StudentModel).all()
        return [StudentResponse(
            id=s.id,
            name=s.name,
            data=s.data or {}
        ) for s in students]
    
    def create(self, student_data):
        # Не указываем ID - PostgreSQL автоматически присвоит следующий
        student = StudentModel(name=student_data.name, data=student_data.data or {})
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return StudentResponse(id=student.id, name=student.name, data=student.data or {})
    
    def delete(self, student_id: int):
        student = self.db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            return None
        self.db.delete(student)
        self.db.commit()
        return {"message": f"Student {student.name} deleted"}
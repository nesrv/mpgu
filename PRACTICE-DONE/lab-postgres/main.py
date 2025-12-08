from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text, MetaData, Table, select
from database import get_db, engine
from pydantic import BaseModel
from schemas import SQLQuery

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Lab PostgreSQL API is running"}

def get_active_students_table():
    metadata = MetaData()
    return Table('active_students_view', metadata, autoload_with=engine)


@app.post("/sql", summary="Execute SQL Query", description="Execute any SQL query and get results")
def execute_sql_query(sql: SQLQuery, db: Session = Depends(get_db)):
    try:
        # Выполняем запрос (может быть многострочным)
        result = db.execute(text(sql.query))
        db.commit()  
        return {"status": "success", "message": "Query executed successfully"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.post("/sql/file", summary="Execute SQL from file", description="Upload and execute SQL file")
async def execute_sql_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        sql_query = content.decode('utf-8')
        
        # Выполняем все запросы из файла
        result = db.execute(text(sql_query))
        db.commit()       
       
        return {"status": "success", "message": "SQL file executed successfully"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/students/active/raw")
def get_active_students_raw(db: Session = Depends(get_db)):
    """Получение активных студентов через raw SQL"""
    result = db.execute(text("SELECT * FROM active_students_view"))
    students = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "count": len(students), "data": students}

@app.get("/students/active/sqlalchemy")
def get_active_students_sqlalchemy(db: Session = Depends(get_db)):
    """Получение активных студентов через SQLAlchemy"""
    try:
        active_students_table = get_active_students_table()
        stmt = select(active_students_table)
        result = db.execute(stmt)
        students = [dict(row._mapping) for row in result]
        return {"method": "sqlalchemy", "count": len(students), "data": students}
    except Exception as e:
        return {"method": "sqlalchemy", "error": str(e)}
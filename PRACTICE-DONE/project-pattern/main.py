from fastapi import FastAPI
from api import students, courses, fixtures

app = FastAPI()
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(fixtures.router)
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# app = FastAPI()

# origins = ["http://localhost:5173",
#            "http://127.0.0.1:5173"
#            ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class Task(BaseModel):
#     title: str
#     description: str = ""
#     completed: bool = False

# tasks_list = []

# @app.get("/tasks")
# def get_tasks():
#     return tasks_list

# @app.post("/tasks")
# def create_task(task: Task):
#     tasks_list.append(task.model_dump())   # <-- changed here
#     return task

# @app.put("/tasks/{index}")
# def update_task(index: int, task: Task):
#     if 0 <= index < len(tasks_list):
#         tasks_list[index] = task.model_dump()  # <-- and here
#         return {"message": "Task updated", "task": task}
#     raise HTTPException(status_code=404, detail="Task not found")

# @app.delete("/tasks/{index}")
# def delete_task(index: int):
#     if 0 <= index < len(tasks_list):
#         removed = tasks_list.pop(index)
#         return {"message": "Task deleted", "task": removed}
#     raise HTTPException(status_code=404, detail="Task not found")
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./tasks.db"

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# DB model
class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class Task(BaseModel):
    title: str
    description: str = ""
    completed: bool = False

class TaskDB(Task):
    id: int
    class Config:
        from_attributes = True

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tasks", response_model=List[TaskDB])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TaskModel).all()
    return tasks

@app.post("/tasks", response_model=TaskDB)
def create_task(task: Task, db: Session = Depends(get_db)):
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.put("/tasks/{task_id}", response_model=TaskDB)
def update_task(task_id: int, task: Task, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db_task.completed = task.completed
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}

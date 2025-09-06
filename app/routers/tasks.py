from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import SessionLocal, Base, engine
from ..models import Task as TaskModel
from ..schemas import TaskCreate, TaskOut

router = APIRouter(tags=["tasks"])

# # ❗ In-memory store = NOT persistent; perfect for first steps

# _tasks: list[dict] = []
# _auto_id = 0

# class TaskCreate(BaseModel):
#     title: str = Field(..., min_length=1, max_length=200)
#     description: str | None=Field(None, max_length=500)

# class TaskOut(TaskCreate):
#     id: int
#     done: bool = False

# Dev convenience: create tables if missing
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tasks",response_model=TaskOut, summary="Create a new task")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    # """
    # - Validates the JSON body against TaskCreate.
    # - Assigns a new id.
    # - Returns TaskOut (controls Swagger + response shape).
    # """
    # global _auto_id
    # _auto_id += 1
    # item = {"id":_auto_id, "title":payload.title, "description":payload.description, "done":False}
    # _tasks.append(item)
    # return item
    task = TaskModel(title=payload.title, description=payload.description, done=False)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/tasks", response_model=List[TaskOut], summary="List all tasks")
def list_tasks(db: Session = Depends(get_db)):

    # """
    # - Returns all tasks (most recent first just for fun).
    # - response_model=List[TaskOut] builds clean OpenAPI types.
    # """
    # return list(reversed(_tasks))
    return db.query(TaskModel).order_by(TaskModel.id.desc()).all()

@router.post("/tasks/{task_id}/toggle", response_model=TaskOut, summary="Toggle done")
def toggle_task(task_id: int, db : Session=Depends(get_db)):
    # for t in _tasks:
    #     if t["id"] == task_id:
    #         t["done"] = not t["done"]
    #         return t
    # raise HTTPException(status_code=404, detail="Task not found")
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    before = bool(task.done)
    task.done = not before
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=204, summary = "Delete a task")
def delete_task(task_id: int, db : Session = Depends(get_db)):
    task = db.get(TaskModel, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
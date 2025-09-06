from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None=Field(None, max_length=500)

class TaskOut(TaskCreate):
    id: int
    done: bool = False

    class Config:
        from_attributes = True
        

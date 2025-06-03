from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from task_api.infrastructure.db.dependencies import get_current_user
from task_api.api.routes.auth_routes import router as auth_router
from task_api.infrastructure.db.db import get_db
from task_api.api.schemas.schemas import TaskCreate, TaskRead, TaskUpdated, PaginatedResponse
from task_api.infrastructure.db.models import *


app = FastAPI(
    title="Task Manager API",
    version="2.0.1",
    openapi_url="/custom-openapi.json"
    )

tasks = APIRouter(tags=["Задачи 📔"], dependencies=[Depends(get_current_user)])
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@tasks.post("/tasks", response_model=List[TaskRead])
async def add_tasks(
        tasks_list: List[TaskCreate],
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    new_tasks = [
        Task(**task.model_dump(), user_id=current_user.id)
        for task in tasks_list
    ]
    db.add_all(new_tasks)
    await db.commit()
    for task in new_tasks:
        await db.refresh(task)
    return new_tasks


@tasks.get("/tasks", response_model=PaginatedResponse[TaskRead])
async def get_tasks_with_pagination(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=0),
        done: bool | None = Query(False),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    base_query = select(Task).where(Task.user_id == current_user.id)

    if done is not None:
        base_query = base_query.where(Task.done == done)

    total_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = total_result.scalar()

    result = await db.execute(base_query.offset(skip).limit(limit))
    data = result.scalars().all()

    serialized_tasks = [TaskRead.from_orm(task) for task in data]

    return PaginatedResponse[TaskRead](total=total, items=serialized_tasks)


@tasks.get("/tasks/{tasks_id}", response_model=TaskRead)
async def get_tasks(
        tasks_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == tasks_id, Task.user_id == current_user.id, Task.deleted == False))
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@tasks.delete("/tasks/{tasks_id}", response_model=TaskRead)
async def delete_task(
        tasks_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result_delete = await db.execute(select(Task).where(Task.id == tasks_id, Task.user_id == current_user.id, Task.deleted == False))
    tasks_delete = result_delete.scalar_one_or_none()

    if tasks_delete is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_delete.deleted = True
    await db.commit()
    return f"Task {tasks_id} deleted successfully"


@tasks.put("/tasks/{tasks_put_id}", response_model=TaskUpdated)
async def change_one_task(
        tasks_put_id: int,
        task_data: TaskUpdated,
        db: AsyncSession = Depends(get_db),
        current_user = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == tasks_put_id, Task.user_id == current_user.id, Task.deleted == False))
    put_task = result.scalar_one_or_none()

    if put_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    put_task.description = task_data.description
    put_task.done = task_data.done
    await db.commit()

    return put_task


app.include_router(auth_router, prefix="/auth")
app.include_router(tasks)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

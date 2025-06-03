from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from task_api.infrastructure.db.models import Task
from task_api.api.schemas.schemas import TaskCreate


async def create_task(db: AsyncSession, tasks: List[TaskCreate]):
    db_task = [Task(description=task.description, done=task.done) for task in tasks]
    db.add_all(db_task)
    await db.commit()
    for task in db_task:
        await db.refresh(task)
    return db_task


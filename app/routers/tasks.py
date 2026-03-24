from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.auth.jwt import get_current_user

router = APIRouter(tags=["Tasks"])

@router.post("/projects/{project_id}/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: int,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Project).where(models.Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add tasks to this project")

    new_task = models.Task(
        **task_data.dict(),
        project_id=project_id
    )
    db.add(new_task)
    await db.flush()
    await db.refresh(new_task)
    return new_task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Task).where(models.Task.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    
    project_result = await db.execute(
        select(models.Project).where(models.Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    update_data = task_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    await db.refresh(task)
    return task



@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Task).where(models.Task.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    
    project_result = await db.execute(
        select(models.Project).where(models.Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    await db.delete(task)
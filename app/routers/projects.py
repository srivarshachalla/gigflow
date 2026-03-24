from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app import models
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.auth.jwt import get_current_user
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Project)
        .where(models.Project.user_id == current_user.id)
        .options(selectinload(models.Project.tasks))
    )
    return result.scalars().all()



@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_project = models.Project(
        **project_data.dict(),
        user_id=current_user.id
    )
    db.add(new_project)
    await db.flush()
    await db.refresh(new_project)

    result = await db.execute(
        select(models.Project)
        .where(models.Project.id == new_project.id)
        .options(selectinload(models.Project.tasks))
    )
    return result.scalar_one()



@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(selectinload(models.Project.tasks))
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(selectinload(models.Project.tasks))
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")

    update_data = project_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.flush()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Project)
        .where(models.Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")

    await db.delete(project)
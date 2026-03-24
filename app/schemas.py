from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str
    hours_logged: Optional[float] = 0.0
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    hours_logged: Optional[float] = None
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    hours_logged: float
    is_completed: bool

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    hourly_rate: float

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    hourly_rate: float
    status: str
    tasks: List[TaskResponse] = []

    model_config = {"from_attributes": True}



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
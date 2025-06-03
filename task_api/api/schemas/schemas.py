from typing import Optional, List, TypeVar, Generic

from pydantic import BaseModel, ConfigDict
from pydantic.v1.generics import GenericModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    done: bool = False


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] | None
    user_id: int
    deleted: bool
    done: bool


    class Config:
        from_attributes = True


T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    items: List[T]

    model_config = ConfigDict(arbitrary_types_allowed=True)

class PaginatedTasksResponse(BaseModel):
    total: int
    items: List[TaskRead]


class TaskDeleted(BaseModel):
    id: int
    description: str
    done: bool


class TaskUpdated(BaseModel):
    # id: int
    description: str | None = None
    done: bool | None = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str


class UserLogin(BaseModel):
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"







    class Config:
        from_attributes = True

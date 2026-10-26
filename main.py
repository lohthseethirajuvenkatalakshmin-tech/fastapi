from typing import Dict
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict, EmailStr

app = FastAPI(title="Task 1 - User CRUD API", version="1.0.0")

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    age: int = Field(ge=13, le=120)

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    email: str | None = Field(default=None, min_length=5, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    age: int | None = Field(default=None, ge=13, le=120)

class User(UserCreate):
    id: int

users: Dict[int, User] = {}
next_id = 1

@app.get("/")
def root():
    return {"message": "Task 1 User CRUD API is running", "docs": "/docs"}

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    global next_id
    if any(user.email.lower() == payload.email.lower() for user in users.values()):
        raise HTTPException(status_code=409, detail="Email already exists")
    user = User(id=next_id, **payload.model_dump())
    users[next_id] = user
    next_id += 1
    return user

@app.get("/users", response_model=list[User])
def list_users():
    return list(users.values())

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, payload: UserUpdate):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    changes = payload.model_dump(exclude_unset=True)
    if "email" in changes and changes["email"] is not None:
        if any(u.id != user_id and u.email.lower() == changes["email"].lower() for u in users.values()):
            raise HTTPException(status_code=409, detail="Email already exists")
    updated = user.model_copy(update={k: v for k, v in changes.items() if v is not None})
    users[user_id] = updated
    return updated

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    del users[user_id]
    return {"message": f"User {user_id} deleted"}

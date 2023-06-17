import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, status, File
from fastapi import FastAPI, Depends, Request
from fastapi_users import FastAPIUsers

import os

from .base_config import auth_backend
from .manager import get_user_manager
from .models import User
from .schemas import UserRead, UserCreate, UserUpdate


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
# @fastapi_users.get("/protected-route")
# def protected_route(user: User = Depends(current_user)):
#     return f"Hello, {user.username}"
#
# @fastapi_users.get("/unprotected-route")
# def unprotected_route():
#     return f"Hello, anonym"

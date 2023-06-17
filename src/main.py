import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, status, File
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from src.video.router import router as video_router
from src.auth.router import fastapi_users
from src.comment.router import router as comment_router
from src.like.router import router as like_router
from src.auth.base_config import auth_backend
from src.auth.manager import get_user_manager
from src.auth.models import User
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.pages.router import router as pag_pouter
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Videohosting"
)

# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/hello")
def get_hello():
    return "Hello man"

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(video_router)
app.include_router(comment_router)
app.include_router(like_router)
app.include_router(pag_pouter)
# app.include_router(router_users)

# current_user = fastapi_users.current_user()
# @app.get("/protected-route")
# def protected_route(user: User = Depends(current_user)):
#     return f"Hello, {user.username}"
#
# @app.get("/unprotected-route")
# def unprotected_route():
#     return f"Hello, anonym"

if __name__=="__main__":
    uvicorn.run("main:app",host='127.0.0.1', port=8000)





from fastapi import APIRouter, Request, Depends, Form, Response
from fastapi.templating import Jinja2Templates
from jinja2.environment import Template, TemplateStream
from src.video.router import *
from fastapi.responses import RedirectResponse
from src.auth.schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from datetime import datetime, timedelta
from src.user.models import s_user
import jwt
from typing import Annotated
from .scurity import *
from src.video.router import upload_video
from sqlalchemy import insert, select, delete, update, false, or_
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.like.router import *


router = APIRouter(
    prefix="",
    tags=["Pages"]
)
class UserDB(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str

templates = Jinja2Templates(directory="./src/templates")

#region Description
# SECRET_KEY = "hsgdcbaljawh"
# ALGORITHM = "HSA256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: str or None = None

# class User(BaseModel):
#     username: str
#     email: str

# class UserInDB(User):
#     hashed_password: str

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_user(db, username:str):
#     if username in db:
#         user_data= db[username]
#         return UserInDB(**user_data)
    
# def authenticate_user(db, username:str, password: str):
#     user = get_user(db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(data:dict, expires_delta: timedelta or None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)

#     to_encode.update({"exp":expire})
#     encoded_jwt = jwt.decode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
#     return encoded_jwt

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
#         username: str = payload.get("sub")
#         if username is None:
#             return "Ex"
#         token_data = TokenData(username=username)
#     except:
#         return "Ex"
    
#     user = get_user(db, username = token_data.username)
#     if user is None:
#         return "Ex"
#     return user

# @router.post("token")
# async def login_for_access_token (form_data:OAuth2PasswordRequestForm=Depends() ):
#     user = authenticate_user(db, form_data.password)

#     if not user:
#         return "Incorrect name or pass"
#     access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data = {"sub":user.username},
#         expires_delta=access_token_expires)
#     return {"acces_token":access_token, "token_type":"bearer"}

# @router.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user

#endregion

@router.get("/")
def start_page(request: Request):
    return templates.TemplateResponse("start_page.html", {"request": request})

#region Video
@router.get("/base")
def get_base_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@router.get("/all")
def get_search(request: Request, operations=Depends(get_all_videos)):
    return templates.TemplateResponse("search.html", {"request": request, "operations": operations})

@router.get("/video/{video_id}")
async def watch_video(request:Request, video = Depends(watch_video_front), a_session: AsyncSession = Depends(get_async_session)):
    print(video["id"])
    likes_count = await video_like_count(video_id = video["id"], a_session = a_session)
    print(likes_count)
    print(type(likes_count))
    # return templates.TemplateResponse("video.html", {"request": request, "video": video })
    response = templates.TemplateResponse("video.html", {"request": request, "url": video["url"], "likes_count": likes_count, "video_id": video["id"]})
    return response


@router.post("/like_video/{video_id}")
async def like_video(request:Request, video_id: int, current_user: UserDB = Depends(get_current_user_from_cookie), resp = Depends(watch_video),   a_session: AsyncSession = Depends(get_async_session)):
    print(resp.context)
    print("rrrrrrrrrrrrrrr")
    url = resp.context["url"]
    print(video_id)
    resp = await like_dislike(video_id=video_id,user_id = current_user["id"], a_session=a_session)
    likes_count = await video_like_count(video_id = video_id, a_session = a_session)
    return templates.TemplateResponse("video.html", {"request": request, "url": url, "likes_count": likes_count, "video_id": video_id})

#endregion

@router.get("/user/signin")
def signup(req: Request):
    return templates.TemplateResponse("signin.html", {"request": req})
 

@router.post("/signinuser")
async def signin(response: RedirectResponse, a_session: AsyncSession = Depends(get_async_session), username: str = Form(...), password: str = Form(...)):
    query = select(s_user).where(s_user.c.username == username)
    res = await a_session.execute(query)
    result = res.first()
    if result is None:
        return "Must register"
    if verify_password(password, result.hashed_password):
        token = create_access_token(result)
        response = RedirectResponse(url ="/all", status_code=302)
        response.set_cookie(
            key= COOKIE_NAME,
            value=token,
            httponly=True,
            expires=1800
        )
        return response   
    else:
        return  "Invalid password"
    
@router.post("/logout")
async def logout(request:Request, response: Response, current_user: UserDB = Depends(get_current_user_from_cookie)):
    # Also tried following two comment lines
    # response.set_cookie(key="access_token", value="", max_age=1)
    # response.delete_cookie("access_token", domain="localhost")
    response = templates.TemplateResponse("signin.html", {"request": request})
    response.delete_cookie(key=COOKIE_NAME)
    return response

@router.get("/user/signup")
def signup(req:Request):
    return templates.TemplateResponse("signup.html", {"request":req})

@router.post("/signupuser")
async def signup_user(req:Request, a_session: AsyncSession = Depends(get_async_session), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    query = select(s_user).where(or_(s_user.c.username == username, s_user.c.email == email))
    res = await a_session.execute(query)
    result = res.all()
    print(result)
    if len(result) == 0:
        stmt = insert(s_user).values(username=username, email=email, hashed_password = get_password_hash(password))
        await a_session.execute(stmt)
        await a_session.commit()
        return templates.TemplateResponse("user_data.html", {"request":req, "username": username, "email":email})
    else:
        return "Пользователь с такими данными уже существует"


@router.get("/video_post")
def video_post(request:Request):
    return templates.TemplateResponse("video_upload.html", {"request":request})



@router.post("/video_upload")
async def video(current_user: UserDB = Depends(get_current_user_from_cookie),title: str = Form(...), description: str = Form(...), video: UploadFile = File(...), a_session: AsyncSession = Depends(get_async_session)):
    if current_user is None:
        return "Must login"
    res = await upload_video(title=title, description=description, user_id=current_user["id"], file = video, a_session=a_session)
    print(f'{current_user["id"]}')
    print(f'{current_user["username"]}')
    print(f'{current_user["email"]}')
    return res


   
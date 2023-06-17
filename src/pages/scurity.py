from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,Request
from src.config import JWT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# JWT_SECRET = "wjnslErabdwn"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES=3000
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/signin")
COOKIE_NAME = "Authorization"

def create_access_token(user):
    try:
        payload = {
            "id":user.id,
            "username": user.username,
            "email": user.email,
        }
        return jwt.encode(payload, key = JWT_SECRET, algorithm= ALGORITHM)
    except Exception as ex:
        print(str(ex))
        raise ex

def verify_token(token):
    try:
        payload=jwt.decode(token,key=JWT_SECRET)
        return payload
    except Exception as ex:
        print(str(ex))
        raise ex
    
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user_from_token(token:str=Depends(oauth2_scheme)):
    user= verify_token(token)
    return user
 
def get_current_user_from_cookie(request:Request):
    token=request.cookies.get(COOKIE_NAME)
    if token:
        user = verify_token(token)
        return user
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

# Authentication function
def authenticate_user(username: str, password: str):
    if username == "Chowdary" and password == "Chowdary@24":
        return User(username=username, email="john@example.com", full_name="John Doe")
    else:
        return None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

async def get_current_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/token", response_model=dict)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await get_current_user(form_data)
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

from fastapi.responses import RedirectResponse
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from .database import make_connection
from .models.models import (
    UserCreate,
    CreateAMI,
    UpdateLTI,
    CreateLTI,
)

from .utils.authentication import (
    hash_password,
    admin_required,
    verify_password,
    verify_token,
    insert_logs,
    create_access_token,
    oauth2_scheme,
)

app = FastAPI(
    title="AWS Image Manager",
    version="0.1.0",
    description="Manages AWS Images and Launch Templates across 4 AWS accounts",
)


client = make_connection()
db = client["DO_console"]
users_collection = db["users"]


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/register/", tags=["Users"])
async def register(user: UserCreate, token: str = Depends(admin_required)):
    # Only admin users can create other admin users
    if user.is_admin:
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        current_user = users_collection.find_one({"username": payload.get("sub")})
        if not current_user or not current_user.get("is_admin"):
            raise HTTPException(
                status_code=403, detail="Only admins can create other admins"
            )

    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user.password)
    user_data = {
        "username": user.username,
        "hashed_password": hashed_password,
        "is_admin": user.is_admin,  # Set is_admin during registration
    }
    users_collection.insert_one(user_data)
    return {"msg": "User registered successfully"}


@app.post("/token", tags=["Token"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/create_ami", tags=["Create AMI"])
@insert_logs
async def create_ami(
    request: Request, item: CreateAMI, token: str = Depends(oauth2_scheme)
):
    return {"ok": item.dict()}


@app.post("/create_launch_template", tags=["Create Launch template"])
@insert_logs
async def create_launch_template(
    request: Request, item: CreateLTI, token: str = Depends(oauth2_scheme)
):
    return {"ok": item.dict()}


@app.put("/update_launch_template", tags=["Update Launch template"])
@insert_logs
async def update_launch_template(
    request: Request, item: UpdateLTI, token: str = Depends(oauth2_scheme)
):
    return {"ok": item.dict()}

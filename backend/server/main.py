import uvicorn
from pydantic import BaseModel, Field

from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from id_generator.IDGenerator import generator
from settings import settings
from server.crud import insert_url_mapping, get_long_url, delete_url_mapping, get_user, insert_user, get_short_url
from server.security import get_password_hash, verify_password, current_user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

class RegisterSchema(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field()


@app.post("/register_user")
async def register_user(request: RegisterSchema):
    username = request.username
    password = request.password
    existing_user = get_user(username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(password)
    insert_user(username, hashed_password)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    verification_result = verify_password(form_data.password, user["password"], user["_id"])
    if not verification_result:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    verification_result["user"] = user['_id']
    return verification_result


@app.get("/generate_url")
async def generate_url(long_url: str, custom_alias: str = None, user_id: str = Depends(current_user)):
    short_url = get_short_url(long_url)
    if short_url:
        return {"url": short_url }
    if custom_alias:
        new_url = generator.generate_id_for_custom_url(custom_alias)
        if new_url is None:
            raise HTTPException(status_code=400, detail="Custom alias is already in use or invalid")
        full_url = f"{settings.domain_name}{new_url}" if new_url else None
    else:
        new_url = generator.fetch_unused_url()
        full_url = f"{settings.domain_name}{new_url}"

    
    insert_url_mapping(full_url, long_url, user_id)
    return {"url": full_url}

@app.get("/get_long_url")
async def get_long_url_endpoint(short_url: str):
    url_mapping = get_long_url(short_url)
    if not url_mapping:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"url": url_mapping["long_url"]}

@app.delete("/delete_url")
async def delete_url(short_url: str, user_id: str = Depends(current_user)):
    mapping = get_long_url(short_url)
    if not mapping:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if mapping["user"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL")
    
    delete_url_mapping(short_url)
    return {"message": "URL mapping deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    age: int
    phone_number: str

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None

class User(UserBase):
    id: int
    profile_photo: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Remote Server Schemas
class RemoteServerBase(BaseModel):
    hostname: str
    ip_address: str
    username: str
    port: int = 22
    private_key: str

class RemoteServerCreate(RemoteServerBase):
    pass

class RemoteServerUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    username: Optional[str] = None
    port: Optional[int] = None
    private_key: Optional[str] = None

class RemoteServer(RemoteServerBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Command Execution Schemas
class CommandExecute(BaseModel):
    command: str

class CommandOutput(BaseModel):
    output: str
    error: Optional[str] = None
    exit_status: int

class CommandLog(BaseModel):
    id: int
    command: str
    output: str
    error: Optional[str] = None
    exit_status: int
    user_id: int
    server_id: int
    executed_at: datetime

    class Config:
        from_attributes = True 
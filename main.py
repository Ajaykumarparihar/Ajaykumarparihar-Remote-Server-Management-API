from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import timedelta

from . import models, schemas, auth, ssh, email_utils
from .database import engine, get_db
from .config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Remote Server Management API")

# User Authentication Routes
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        age=user.age,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# User Profile Routes
@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

@app.put("/users/me/", response_model=schemas.User)
async def update_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/users/me/profile-photo/")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_location = os.path.join(settings.UPLOAD_DIR, f"profile_{current_user.id}.jpg")
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    current_user.profile_photo = file_location
    db.commit()
    return {"filename": file_location}

# Remote Server Routes
@app.post("/servers/", response_model=schemas.RemoteServer)
async def create_server(
    server: schemas.RemoteServerCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_server = models.RemoteServer(**server.dict(), owner_id=current_user.id)
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server

@app.get("/servers/", response_model=List[schemas.RemoteServer])
async def read_servers(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(models.RemoteServer).filter(models.RemoteServer.owner_id == current_user.id).all()

@app.get("/servers/{server_id}", response_model=schemas.RemoteServer)
async def read_server(
    server_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    server = db.query(models.RemoteServer).filter(
        models.RemoteServer.id == server_id,
        models.RemoteServer.owner_id == current_user.id
    ).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@app.put("/servers/{server_id}", response_model=schemas.RemoteServer)
async def update_server(
    server_id: int,
    server_update: schemas.RemoteServerUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    server = db.query(models.RemoteServer).filter(
        models.RemoteServer.id == server_id,
        models.RemoteServer.owner_id == current_user.id
    ).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    
    for field, value in server_update.dict(exclude_unset=True).items():
        setattr(server, field, value)
    db.commit()
    db.refresh(server)
    return server

@app.delete("/servers/{server_id}")
async def delete_server(
    server_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    server = db.query(models.RemoteServer).filter(
        models.RemoteServer.id == server_id,
        models.RemoteServer.owner_id == current_user.id
    ).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db.delete(server)
    db.commit()
    return {"message": "Server deleted successfully"}

# Command Execution Routes
@app.post("/servers/{server_id}/execute", response_model=schemas.CommandOutput)
async def execute_command(
    server_id: int,
    command: schemas.CommandExecute,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    server = db.query(models.RemoteServer).filter(
        models.RemoteServer.id == server_id,
        models.RemoteServer.owner_id == current_user.id
    ).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    
    try:
        output, error, exit_status = ssh.execute_ssh_command(server, command.command)
        
        # Log the command execution
        command_log = models.CommandLog(
            command=command.command,
            output=output,
            error=error,
            exit_status=exit_status,
            user_id=current_user.id,
            server_id=server.id
        )
        db.add(command_log)
        db.commit()
        
        # Send email notification
        await email_utils.send_command_execution_email(
            current_user, server, command.command, output, error, exit_status
        )
        
        return schemas.CommandOutput(
            output=output,
            error=error,
            exit_status=exit_status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_id}/logs", response_model=List[schemas.CommandLog])
async def get_command_logs(
    server_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    server = db.query(models.RemoteServer).filter(
        models.RemoteServer.id == server_id,
        models.RemoteServer.owner_id == current_user.id
    ).first()
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return db.query(models.CommandLog).filter(
        models.CommandLog.server_id == server_id,
        models.CommandLog.user_id == current_user.id
    ).all() 
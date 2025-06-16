from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    phone_number = Column(String)
    profile_photo = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    servers = relationship("RemoteServer", back_populates="owner")
    command_logs = relationship("CommandLog", back_populates="user")

class RemoteServer(Base):
    __tablename__ = "remote_servers"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    ip_address = Column(String)
    username = Column(String)
    port = Column(Integer, default=22)
    private_key = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="servers")
    command_logs = relationship("CommandLog", back_populates="server")

class CommandLog(Base):
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True, index=True)
    command = Column(String)
    output = Column(Text)
    error = Column(Text, nullable=True)
    exit_status = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    server_id = Column(Integer, ForeignKey("remote_servers.id"))
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="command_logs")
    server = relationship("RemoteServer", back_populates="command_logs") 
#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "uvicorn",
#   "fastapi[standard]",
#   "sqlalchemy"
# ]
# ///

###############################################################################
#
# Very basic application that expose a couple of endpoints that you can
# use to test fault.
# Once you have installed `uv` https://docs.astral.sh/uv/, simply run the
# application as follows:
# 
# uv run --script app.py
#
###############################################################################
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Body
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError


###############################################################################
# Database configuration
###############################################################################
uri = "postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase"
engine = create_engine(uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


###############################################################################
# Data model
###############################################################################
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)


###############################################################################
# Dependency injection
###############################################################################
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


###############################################################################
# Our application
###############################################################################
app = FastAPI(servers=[{"url": "http://localhost:9090"}])


@app.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello, World!"}


@app.post("/users/")
async def create_user(
    name: Annotated[str, Body()],
    password: Annotated[str, Body()],
    db: sessionmaker[Session] = Depends(get_db)
):
    db_user = User(name=name, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get("/users/{user_id}")
async def read_user(
    user_id: int, db: sessionmaker[Session] = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == "__main__":
    uvicorn.run("app:app", port=9090)

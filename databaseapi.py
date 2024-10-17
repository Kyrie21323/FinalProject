from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, index=True)
    platform = Column(String, index=True)
    url = Column(String, index=True)
    title = Column(String, index=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Replace with your database URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import models, database

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/contents/", response_model=List[models.Content])
def read_contents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    contents = db.query(models.Content).offset(skip).limit(limit).all()
    return contents

@app.get("/contents/{content_id}", response_model=models.Content)
def read_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@app.post("/contents/", response_model=models.Content)
def create_content(content: models.Content, db: Session = Depends(get_db)):
    db.add(content)
    db.commit()
    db.refresh(content)
    return content

@app.put("/contents/{content_id}", response_model=models.Content)
def update_content(content_id: int, updated_content: models.Content, db: Session = Depends(get_db)):
    content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    for key, value in updated_content.dict().items():
        setattr(content, key, value)
    db.commit()
    db.refresh(content)
    return content

@app.delete("/contents/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    db.delete(content)
    db.commit()
    return {"detail": "Content deleted"}

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from ..database import get_db
from ..models.challenge import Challenge
from ..schemas.challenge import ChallengeCreate, Challenge as ChallengeSchema
from ..auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.post("/challenges/", response_model=ChallengeSchema)
def create_challenge(
    challenge: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_challenge = Challenge(
        title=challenge.title,
        description=challenge.description,
        latitude=challenge.latitude,
        longitude=challenge.longitude,
        boundary=challenge.boundary,
        user_id=current_user.id
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

@router.get("/challenges/", response_model=List[ChallengeSchema])
def get_challenges(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    challenges = db.query(Challenge).offset(skip).limit(limit).all()
    return challenges

@router.get("/challenges/{challenge_id}", response_model=ChallengeSchema)
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge

@router.post("/challenges/{challenge_id}/photo")
async def upload_challenge_photo(
    challenge_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if challenge.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to upload photo for this challenge")
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/challenges"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, f"{challenge_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update challenge with photo path
    challenge.photo_path = file_path
    db.commit()
    
    return {"message": "Photo uploaded successfully", "file_path": file_path} 
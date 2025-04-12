from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChallengeBase(BaseModel):
    title: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    boundary: Optional[Dict[str, Any]] = None

class ChallengeCreate(ChallengeBase):
    pass

class Challenge(ChallengeBase):
    id: int
    user_id: int
    photo_path: Optional[str] = None

    class Config:
        orm_mode = True 
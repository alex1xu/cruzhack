from datetime import datetime
from typing import List, Dict, Any
import numpy as np
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from database import Base
import json

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    photo_path = Column(String(255))
    boundary = Column(Text)  # Store GeoJSON as string
    latitude = Column(Float)
    longitude = Column(Float)

    user = relationship("User", back_populates="challenges")
    guesses = relationship("Guess", back_populates="challenge")

    def __init__(self, user_id: str, location: Dict[str, float], 
                 embedding: np.ndarray, caption: str):
        self.user_id = user_id
        self.location = location
        self.embedding = embedding
        self.caption = caption
        self.created_at = datetime.utcnow()
        self.leaderboard = []  # List of {'user_id': str, 'guesses': int}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "photo_path": self.photo_path,
            "boundary": json.loads(self.boundary) if self.boundary else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            'created_at': self.created_at.isoformat(),
            'leaderboard': self.leaderboard
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Challenge':
        challenge = cls(
            user_id=data['user_id'],
            location=data['location'],
            embedding=np.array(data['embedding']),
            caption=data['caption']
        )
        challenge.created_at = datetime.fromisoformat(data['created_at'])
        challenge.leaderboard = data.get('leaderboard', [])
        return challenge 
from datetime import datetime
from typing import List, Dict, Any
# import numpy as np
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
import json
# from geojson_pydantic import Polygon

class Challenge:
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    photo_path = Column(String(255))
    boundary = Column(Text)  # Store GeoJSON as string

    user = relationship("User", back_populates="challenges")
    guesses = relationship("Guess", back_populates="challenge")

    def __init__(self, user_id: str, title: str, description: str, boundary: str):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.boundary = boundary
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
            'created_at': self.created_at.isoformat(),
            'leaderboard': self.leaderboard
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Challenge':
        challenge = cls(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description'),
            boundary=json.dumps(data['boundary'])
        )
        challenge.created_at = datetime.fromisoformat(data['created_at'])
        challenge.leaderboard = data.get('leaderboard', [])
        return challenge 
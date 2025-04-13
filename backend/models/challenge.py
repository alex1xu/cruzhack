from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import numpy as np
from sqlalchemy import Column, Integer, String, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
# from geojson_pydantic import Polygon

class Challenge:
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    photo_path = Column(String(255))
    boundary = Column(Text)  # Store GeoJSON as string
    embedding = Column(LargeBinary)  # Store embedding as binary
    caption = Column(Text)

    user = relationship("User", back_populates="challenges")
    guesses = relationship("Guess", back_populates="challenge")

    def __init__(
        self,
        user_id: str,
        title: str,
        description: str,
        boundary: str,
        photo_path: Optional[str] = None,
        embedding: Optional[np.ndarray] = None,
        caption: Optional[str] = None
    ):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.boundary = boundary
        self.photo_path = photo_path
        self.embedding = embedding
        self.caption = caption
        self.created_at = datetime.utcnow()
        self.leaderboard = []  # List of {'user_id': str, 'username': str, 'guesses': int}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(getattr(self, '_id', '')),
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "photo_path": self.photo_path,
            "boundary": json.loads(self.boundary) if self.boundary else None,
            "embedding": self.embedding.tolist() if isinstance(self.embedding, np.ndarray) else None,
            "caption": self.caption,
            "created_at": self.created_at.isoformat() if hasattr(self, 'created_at') else None,
            "leaderboard": getattr(self, 'leaderboard', [])
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Challenge':
    # Convert embedding from list to numpy array if it exists
        embedding = None
        if data.get('embedding') is not None:
            try:
                embedding = np.array(data['embedding'], dtype=np.float32)
            except Exception as e:
                print(f"Error converting embedding: {str(e)}")
                embedding = None

        challenge = cls(
            user_id=str(data['user_id']),
            title=data['title'],
            description=data.get('description', ''),
            boundary=json.dumps(data.get('boundary', {})),
            photo_path=data.get('photo_path'),
            embedding=embedding,
            caption=data.get('caption')
        )
        challenge._id = data.get('_id')
        if 'created_at' in data and data['created_at']:
            challenge.created_at = datetime.fromisoformat(data['created_at'])
        else:
            challenge.created_at = datetime.utcnow()
        challenge.leaderboard = data.get('leaderboard', [])
        return challenge 
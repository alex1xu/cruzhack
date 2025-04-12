from datetime import datetime
from typing import List, Dict, Any
import numpy as np

class Challenge:
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
            'user_id': self.user_id,
            'location': self.location,
            'caption': self.caption,
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
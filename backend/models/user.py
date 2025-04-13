from datetime import datetime
from typing import Dict, Any
import bcrypt
import re

class User:
    def __init__(self, username: str, password: str, is_login: bool = False, _id: str = None):
        if not self._validate_username(username):
            raise ValueError("Invalid username format")
        if not is_login and not self._validate_password(password):
            raise ValueError("Invalid password format")
            
        self.username = username
        self.password_hash = self._hash_password(password)
        self.created_at = datetime.utcnow()
        self._id = _id
        self.stats = {
            'challenges_created': 0,
            'challenges_solved': 0,
            'total_guesses': 0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'username': self.username,
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat(),
            'stats': self.stats
        }
        if self._id:
            result['_id'] = self._id
        return result
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        user = cls(
            username=data['username'],
            password="dummy",  # Password is not stored in plain text
            is_login=True,  # Skip password validation when loading from DB
            _id=str(data.get('_id')) if data.get('_id') else None
        )
        user.password_hash = data['password_hash']
        user.created_at = datetime.fromisoformat(data['created_at'])
        user.stats = data.get('stats', {
            'challenges_created': 0,
            'challenges_solved': 0,
            'total_guesses': 0
        })
        return user
        
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
        
    def _hash_password(self, password: str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
    @staticmethod
    def _validate_username(username: str) -> bool:
        # Username must be 3-20 characters, alphanumeric with underscores
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
        
    @staticmethod
    def _validate_password(password: str) -> bool:
        # Password must be at least 8 characters, contain at least one number,
        # one uppercase letter, and one lowercase letter
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
        return bool(re.match(pattern, password)) 
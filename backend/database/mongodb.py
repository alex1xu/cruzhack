from pymongo import MongoClient
from typing import List, Optional
import os
from models.challenge import Challenge
from models.user import User
from bson import ObjectId
from datetime import datetime
from typing import Dict, List

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['challenge_app']
        self.challenges = self.db['challenges']
        self.users = self.db['users']
        
        self.users.create_index('username', unique=True)
        
    def save_challenge(self, challenge: Challenge) -> str:
        challenge_dict = challenge.to_dict()
        if challenge_dict.get('embedding') is not None:
            challenge_dict['embedding'] = challenge_dict['embedding'].tolist()
        result = self.challenges.insert_one(challenge_dict)
        return str(result.inserted_id)
        
    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        try:
            challenge_data = self.challenges.find_one({'_id': ObjectId(challenge_id)})
            if challenge_data:
                return Challenge.from_dict(challenge_data)
            return None
        except Exception:
            return None
        
    def get_all_challenges(self) -> List[Challenge]:
        challenges = self.challenges.find()
        return [Challenge.from_dict(challenge) for challenge in challenges]
        
    def update_leaderboard(self, challenge_id: str, user_id: str, username: str, guesses: int):
        try:
            # Find existing entry for user
            challenge = self.challenges.find_one({'_id': ObjectId(challenge_id)})
            if not challenge:
                return
                
            leaderboard = challenge.get('leaderboard', [])
            user_entry = next((entry for entry in leaderboard if entry['user_id'] == user_id), None)
            
            if user_entry:
                # Update if new score is better
                if guesses < user_entry['guesses']:
                    self.challenges.update_one(
                        {'_id': ObjectId(challenge_id), 'leaderboard.user_id': user_id},
                        {'$set': {'leaderboard.$.guesses': guesses}}
                    )
            else:
                # Add new entry
                self.challenges.update_one(
                    {'_id': ObjectId(challenge_id)},
                    {'$push': {'leaderboard': {
                        'user_id': user_id,
                        'username': username,
                        'guesses': guesses
                    }}}
                )
        except Exception as e:
            print(f"Error updating leaderboard: {str(e)}")
        
    def get_leaderboard(self, challenge_id: str) -> List[Dict]:
        try:
            challenge = self.challenges.find_one({'_id': ObjectId(challenge_id)})
            if not challenge:
                return []
                
            leaderboard = challenge.get('leaderboard', [])
            # Sort by number of guesses (ascending)
            leaderboard.sort(key=lambda x: x['guesses'])
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {str(e)}")
            return []
        
    def save_user(self, user: User) -> str:
        try:
            result = self.users.insert_one(user.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            if 'duplicate key error' in str(e):
                raise ValueError("Username already exists")
            raise e
        
    def get_user(self, user_id: str) -> Optional[User]:
        user_data = self.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User.from_dict(user_data)
        return None
        
    def get_user_by_username(self, username: str) -> Optional[User]:
        user_data = self.users.find_one({'username': username})
        if user_data:
            return User.from_dict(user_data)
        return None
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if user and user.verify_password(password):
            return user
        return None 
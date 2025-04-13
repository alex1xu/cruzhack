from pymongo import MongoClient
from typing import List, Optional
import os
from models.challenge import Challenge
from models.user import User
from bson import ObjectId
from datetime import datetime
from typing import Dict, List
import numpy as np

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['challenge_app']
        self.challenges = self.db['challenges']
        self.users = self.db['users']
        
        self.users.create_index('username', unique=True)
        
    def save_challenge(self, challenge: Challenge) -> str:
        try:
            challenge_dict = challenge.to_dict()
            # Ensure embedding is properly converted to list
            if challenge_dict.get('embedding') is not None:
                if isinstance(challenge_dict['embedding'], np.ndarray):
                    challenge_dict['embedding'] = challenge_dict['embedding'].tolist()
                elif not isinstance(challenge_dict['embedding'], list):
                    print("Warning: embedding is not in expected format")
                    challenge_dict['embedding'] = None
            result = self.challenges.insert_one(challenge_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving challenge: {str(e)}")
            raise
        
    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        try:
            challenge_data = self.challenges.find_one({'_id': ObjectId(challenge_id)})
            if challenge_data:
                # Ensure embedding is properly converted to numpy array
                if challenge_data.get('embedding') is not None:
                    try:
                        challenge_data['embedding'] = np.array(challenge_data['embedding'])
                    except Exception as e:
                        print(f"Error converting embedding: {str(e)}")
                        challenge_data['embedding'] = None
                return Challenge.from_dict(challenge_data)
            return None
        except Exception as e:
            print(f"Error getting challenge: {str(e)}")
            return None
        
    def get_all_challenges(self) -> List[Challenge]:
        try:
            challenges = self.challenges.find()
            result = []
            for challenge in challenges:
                # Ensure embedding is properly converted to numpy array
                if challenge.get('embedding') is not None:
                    try:
                        challenge['embedding'] = np.array(challenge['embedding'])
                    except Exception as e:
                        print(f"Error converting embedding: {str(e)}")
                        challenge['embedding'] = None
                result.append(Challenge.from_dict(challenge))
            return result
        except Exception as e:
            print(f"Error getting all challenges: {str(e)}")
            return []
        
    def update_leaderboard(self, challenge_id: str, user_id: str, username: str, guesses: int):
        try:
            # Find the challenge document by its ObjectId
            challenge = self.challenges.find_one({'_id': ObjectId(challenge_id)})
            if not challenge:
                print(f"Challenge with id {challenge_id} not found.")
                return
            
            # Ensure that the leaderboard field exists and is a list
            if 'leaderboard' not in challenge or challenge['leaderboard'] is None:
                self.challenges.update_one(
                    {'_id': ObjectId(challenge_id)},
                    {'$set': {'leaderboard': []}}
                )
                challenge['leaderboard'] = []

            leaderboard = challenge.get('leaderboard', [])
            # Find an existing entry for this user in the leaderboard
            user_entry = next((entry for entry in leaderboard if entry.get('user_id') == user_id), None)

            if user_entry:
                # Update if the new score is better (i.e., lower guess count)
                if guesses < user_entry.get('guess_count', float('inf')):
                    result = self.challenges.update_one(
                        {'_id': ObjectId(challenge_id), 'leaderboard.user_id': user_id},
                        {'$set': {
                            'leaderboard.$.guess_count': guesses,
                            'leaderboard.$.username': username  # update username if necessary
                        }}
                    )
                    print(f"Leaderboard updated for user {user_id}: matched {result.matched_count}, modified {result.modified_count}")
                else:
                    print("New guess count is not lower than the existing score; leaderboard not updated.")
            else:
                # Add a new leaderboard entry for this user
                result = self.challenges.update_one(
                    {'_id': ObjectId(challenge_id)},
                    {'$push': {'leaderboard': {
                        'user_id': user_id,
                        'username': username,
                        'guess_count': guesses
                    }}}
                )
                print(f"Added new leaderboard entry for user {user_id}: matched {result.matched_count}, modified {result.modified_count}")
        except Exception as e:
            print(str(e))
            print(f"Error updating leaderboard: {str(e)}")

    def get_leaderboard(self, challenge_id: str) -> List[Dict]:
        try:
            challenge = self.challenges.find_one({'_id': ObjectId(challenge_id)})
            if not challenge:
                return []
                
            leaderboard = challenge.get('leaderboard', [])
            # Sort by number of guesses (ascending)
            leaderboard.sort(key=lambda x: x['guess_count'])
            return leaderboard
        except Exception as e:
            print(f"Error getting leaderboard: {str(e)}")
            return []
        
    def save_user(self, user: User) -> str:
        try:
            user_dict = user.to_dict()
            if '_id' in user_dict:
                del user_dict['_id']  # Remove _id if it exists to let MongoDB generate a new one
            result = self.users.insert_one(user_dict)
            return str(result.inserted_id)
        except Exception as e:
            if 'duplicate key error' in str(e):
                raise ValueError("Username already exists")
            raise e
        
    def get_user(self, user_id: str) -> Optional[User]:
        try:
            user_data = self.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
        
    def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            user_data = self.users.find_one({'username': username})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by username: {str(e)}")
            return None
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        try:
            user_data = self.users.find_one({'username': username})
            if user_data:
                user = User.from_dict(user_data)
                if user.verify_password(password):
                    return user
            return None
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None 
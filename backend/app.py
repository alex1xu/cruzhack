from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from models.challenge import Challenge
from models.user import User
from services.embedding_service import EmbeddingService
from services.gemini_service import GeminiService
from database.mongodb import MongoDB
import magic
from werkzeug.utils import secure_filename
from typing import Dict, List
import numpy as np

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
db = MongoDB()
embedding_service = EmbeddingService()
gemini_service = GeminiService()

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    if not file:
        return False, "No file provided"
    if not allowed_file(file.filename):
        return False, "Invalid file type"
    if file.content_length and file.content_length > MAX_CONTENT_LENGTH:
        return False, "File too large"
        
    # Check MIME type using the first 1024 bytes
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file.read(1024))
    file.seek(0)
    
    if not file_mime.startswith('image/'):
        return False, "Invalid file type"
        
    return True, None

# -------------------------------
# Authentication endpoints
# -------------------------------
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        user = User(username=username, password=password)
        user_id = db.save_user(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        user = db.authenticate_user(username, password)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
            
        return jsonify({
            'message': 'Login successful',
            'user_id': user._id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------
# Challenge endpoints
# -------------------------------

@app.route('/api/challenges', methods=['POST'])
def create_challenge():
    try:
        # Get form data
        user_id = request.form.get('user_id')
        title = request.form.get('title')
        description = request.form.get('description')
        boundary = request.form.get('boundary')
        photo = request.files.get('photo')

        if not all([user_id, title, description, boundary, photo]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate image
        is_valid, error = validate_image(photo)
        if not is_valid:
            return jsonify({'error': error}), 400
            
        # Save photo
        filename = secure_filename(photo.filename)
        photo_path = os.path.join('uploads', filename)
        os.makedirs('uploads', exist_ok=True)
        photo.save(photo_path)

        # Generate caption using Gemini
        caption = gemini_service.generate_caption(photo_path)

        # prepend a riddle to description
        description = description+'\n\n'+gemini_service.generate_riddle(photo_path) 

        # Create challenge
        challenge = Challenge(
            user_id=user_id,
            title=title,
            description=description,
            boundary=boundary,
            photo_path=photo_path,
            caption=caption
        )

        # Save to the database
        challenge_id = db.save_challenge(challenge)

        return jsonify({
            'message': 'Challenge created successfully',
            'challenge_id': str(challenge_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges', methods=['GET'])
def get_challenges():
    try:
        challenges = db.get_all_challenges()
        return jsonify([challenge.to_dict() for challenge in challenges])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges/<challenge_id>/guess', methods=['POST'])
def submit_guess(challenge_id):
    try:
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        photo = request.files.get('photo')
        guess_count = int(request.form.get('guess_count', 1))

        if not all([user_id, photo]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Validate image
        is_valid, error = validate_image(photo)
        if not is_valid:
            return jsonify({'error': error}), 400
            
        # Retrieve challenge from DB
        challenge = db.get_challenge(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        # Save guess photo
        filename = secure_filename(photo.filename)
        guess_photo_path = os.path.join('uploads', f'guess_{filename}')
        photo.save(guess_photo_path)
        
        # Get captions
        answer_caption = challenge.caption
        guess_caption = gemini_service.generate_caption(guess_photo_path)

        # print('ac',answer_caption,'gc', guess_caption)

        # Calculate similarities
        img_similarity_score = embedding_service.img_similarity(guess_photo_path, challenge.photo_path)
        text_similarity_score = embedding_service.caption_similarity(guess_caption, answer_caption)
        metric_similarity = embedding_service.metric_similarity(img_similarity_score, text_similarity_score)

        # print('is',img_similarity_score)
        # print('ts',text_similarity_score)
        # print('ms',metric_similarity)
        
        # Check object match
        match = embedding_service.object_match(guess_photo_path, answer_caption)
        
        # print('match',match)

        # Determine if guess is correct
        is_correct = embedding_service.decision_threshold(match, metric_similarity)

        if is_correct:
            # Update leaderboard if guess is correct
            db.update_leaderboard(challenge_id, user_id, username, guess_count)
            feedback = "Congratulations! You've solved the challenge!"
        else:
            # Generate a hint using the Gemini service
            feedback = gemini_service.generate_hint(challenge.photo_path, guess_photo_path)
            
        return jsonify({
            'correct': is_correct,
            'feedback': feedback,
            'similarity': float(metric_similarity)
        })
        
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges/<challenge_id>/leaderboard', methods=['GET'])
def get_leaderboard(challenge_id):
    try:
        leaderboard = db.get_leaderboard(challenge_id)
        return jsonify(leaderboard)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges/<challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """
    Retrieves a single challenge by its ID.
    """
    try:
        challenge = db.get_challenge(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        return jsonify(challenge.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

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
    if file.content_length > MAX_CONTENT_LENGTH:
        return False, "File too large"
        
    # Check MIME type
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file.read(1024))
    file.seek(0)
    
    if not file_mime.startswith('image/'):
        return False, "Invalid file type"
        
    return True, None

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
            'user_id': str(user._id)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges', methods=['POST'])
def create_challenge():
    try:
        user_id = request.form.get('user_id')
        photo = request.files.get('photo')

        if not all([user_id, photo]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Validate image
        is_valid, error = validate_image(photo)
        if not is_valid:
            return jsonify({'error': error}), 400
            
        # Generate embedding and caption
        embedding, caption = embedding_service.process_image(photo)
        
        # Create challenge
        challenge = Challenge(
            user_id=user_id,
            location={'lat': 0, 'lng': 0},
            embedding=embedding,
            caption=caption
        )

        # Save to database
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
        photo = request.files.get('photo')
        guess_count = int(request.form.get('guess_count', 1))
        
        if not all([user_id, photo]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Validate image
        is_valid, error = validate_image(photo)
        if not is_valid:
            return jsonify({'error': error}), 400
            
        # Get challenge
        challenge = db.get_challenge(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
            
        # Process guess image
        guess_embedding, guess_caption = embedding_service.process_image(photo)
        
        # Calculate similarity
        similarity = embedding_service.calculate_similarity(
            challenge.embedding, 
            guess_embedding
        )
        
        # Check if guess is correct
        is_correct = similarity > 0.8  # Adjust threshold as needed
        
        if is_correct:
            # Update leaderboard
            db.update_leaderboard(challenge_id, user_id, guess_count)
            hint = "Congratulations! You've solved the challenge!"
        else:
            # Generate hint
            hint = gemini_service.generate_hint(challenge.caption, guess_caption)
            
        return jsonify({
            'is_correct': is_correct,
            'hint': hint,
            'similarity': float(similarity)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenges/<challenge_id>/leaderboard', methods=['GET'])
def get_leaderboard(challenge_id):
    try:
        leaderboard = db.get_leaderboard(challenge_id)
        return jsonify(leaderboard)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
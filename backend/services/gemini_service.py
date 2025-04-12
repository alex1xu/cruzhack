import google.generativeai as genai
import os

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_hint(self, answer_caption: str, guess_caption: str) -> str:
        prompt = f"""
        You are a helpful hint generator for a photo guessing game.
        
        The correct answer is: {answer_caption}
        The player's guess is: {guess_caption}
        
        Generate a helpful hint that:
        1. Doesn't reveal the answer directly
        2. Points the player in the right direction
        3. Is encouraging and constructive
        4. Is concise (1-2 sentences)
        
        Hint:
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip() 
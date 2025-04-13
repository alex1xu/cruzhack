import google.generativeai as genai
import os
from PIL import Image

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_caption(self, photo_path: str) -> str:
        # Load the image
        image = Image.open(photo_path)
        
        # Generate caption using the vision model
        response = self.model.generate_content([
            "Generate a short, concise, and descriptive caption for this image. Focus on the main subject and key details.",
            image
        ])
        
        return response.text.strip() 
    
    def generate_hint_caption(self, photo_path: str) -> str:
        # Load the image
        image = Image.open(photo_path)
        
        prompt = """
        Describe this image in detail. Focus on:
        1. The central/main subject
        2. The surrounding environment
        3. Key distinguishing features
        4. The overall setting and context
        """
        
        response = self.model.generate_content([prompt, image])
        return response.text.strip()
        
    def generate_hint(self, answer_photo: str, guess_photo: str) -> str:
        answer_caption = self.generate_hint_caption(answer_photo)
        guess_caption = self.generate_hint_caption(guess_photo)

        prompt = f"""
        You are generating a hint for a user in a photo scavenger hunt game.

        Here are examples:
        - Photo inputs: Two separate images of Apple Park. One is the front entrance, the other is a more far away view.
         Hint: "You are right!"

        - Photo inputs: Goal photo is a lighthouse, and user's photo is a beach.
            Hint: "Look for a structure that stands tall and contrasts with the open, flowing surroundings. Pay attention to where solid shapes meet open horizons."
  
        - Photo inputs: Goal photo is the Golden Gate Bridge, user's photo is the Bay Bridge.
        Hint: "Pay attention to a structure that feels more vivid and iconic, with softer arches rising sharply against a broader horizon."

        - Photo inputs: Goal photo is Lighthouse Point (brick lighthouse), user's photo is Walton Light (white lighthouse on rocks).
        Hint: "Look for a structure that feels more grounded and historic, set back from the immediate edge of the water. Notice the heavier, earthy materials and the open grassy surroundings nearby."

        - Photo inputs: Two separate images of Chase Center. One is the view from a boat on the SF Bay, the other is an aerial view of the building.
        Hint: "You are right!"

        Now, here is a new case:
        Goal photo is {answer_caption}, user's photo is {guess_caption}

        **Instructions:**
        - Talk to the user in first person.
        - Write a hint to help them find the main object from the goal image.
        - The goal image is always the first image.
        - Keep in mind that the user cannot see the goal image, so do not assume that they know what you're talking about. 
        - The hint should be 1–2 sentences only.
        - If the main object has been captured, please say "You are right!"
        - Focus on subtle differences like color, structure, setting, feel.
        - If the only difference is color, you can point it out gently.
        - DO NOT compliment the user.
        - DO NOT reveal exact object names.
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip() 
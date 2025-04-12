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
        {answer_caption}, {guess_caption}

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
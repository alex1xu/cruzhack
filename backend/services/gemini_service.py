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

    def generate_riddle(self, photo_path: str) -> str:
        image = Image.open(photo_path)

        prompt = """You are generating a riddle for a user in a photo scavenger hunt game.

        - Goal image: Lighthouse Point in Santa Cruz. Riddle: "Built from clay and crowned with glass,I face the tides that surfers pass.Though no ships heed my silent call,My heart still shines beside the squall."
        - Goal image: The Golden Gate Bridge. Riddle: "A road that spans the bay, With cables that stretch and sway. A symbol of the City's grace, Where the sea meets the sky."
        - Goal image: The Chicago Bean. Riddle: "I am not food, though many think so. I curve and shine, reflecting all you know. Beneath the city’s towering gaze, I capture faces in twisted ways."
        - Goal image: A random willow tree, you may not know where it is from. Riddle: "My arms hang low and sweep the ground, Yet I stand tall without a sound. Soft and slow, I dance with air, Near waters calm and gardens fair."

        generate a riddle for finding the main object from the following image: 
        NOTE: NEVER INCLUDE IN YOUR RIDDLE ANYTHING ABOUT THE TIME OF DAY. 
        choose one, and then output it. Only output the riddle, no other text.
        """

        response = self.model.generate_content([
            prompt,
            image
        ])
        
        return response.text.strip() 

    def generate_caption(self, photo_path: str) -> str:
        # Load the image
        image = Image.open(photo_path)
        
        # Generate caption using the vision model
        response = self.model.generate_content([
            "Generate a short, concise, and descriptive caption for this image. Focus on the main subject and key details. NEVER FOCUS ON THE TIME OF DAY.",
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
        3. NEVER FOCUS ON THE TIME OF DAY.
        4. Key distinguishing features
        5. The overall setting and context
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
        - THE HINT SHOULD NEVER BE ABOUT THE TIME OF DAY.
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
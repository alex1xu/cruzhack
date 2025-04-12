import torch
from torchvision import transforms
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
import os

class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.to(self.device)
        
    def process_image(self, image_file) -> tuple[np.ndarray, str]:
        # Load and preprocess image
        image = Image.open(image_file).convert('RGB')
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate image embedding
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=1, keepdim=True)
            
        # Generate caption
        caption = self._generate_caption(image)
        
        return image_features.cpu().numpy()[0], caption
        
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        return float(similarity)
        
    def _generate_caption(self, image: Image.Image) -> str:
        # Simple caption generation using CLIP
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            text_features = self.model.get_text_features(
                self.processor(
                    text=["a photo of"],
                    return_tensors="pt",
                    padding=True
                ).to(self.device)
            )
            
            # Calculate similarity with some common captions
            similarities = torch.matmul(image_features, text_features.T)
            caption_idx = similarities.argmax().item()
            
            # Return a simple caption
            return "A photo of an object or scene" 
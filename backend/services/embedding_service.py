import torch
from torchvision import transforms
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
import os

cache_dir = "./clip_cache"
MAX_SEQUENCE_LENGTH = 77  # CLIP's maximum sequence length

class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", cache_dir=cache_dir)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", cache_dir=cache_dir)
        self.model.to(self.device)
        
    def _truncate_text(self, text: str) -> str:
        # Tokenize the text
        tokens = self.processor.tokenizer(text, return_tensors="pt", truncation=False)
        # If the sequence is too long, truncate it
        if len(tokens['input_ids'][0]) > MAX_SEQUENCE_LENGTH:
            truncated_tokens = tokens['input_ids'][0][:MAX_SEQUENCE_LENGTH]
            return self.processor.tokenizer.decode(truncated_tokens)
        return text
        
    def process_image(self, image_file) -> tuple[np.ndarray, str]:
        # Load and preprocess image
        image = Image.open(image_file).convert('RGB')
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate image embedding
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            image_features = image_features / image_features.norm(dim=1, keepdim=True)
            
        # # Generate caption
        caption = self._generate_caption(image)

        return image_features.cpu().numpy()[0], caption
        
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        # Calculate cosine similarity between two embeddings
        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return float(similarity)
        
    def object_match(self, guess_image_path: str, answer_caption: str) -> float:
        # Truncate the caption if needed
        answer_caption = self._truncate_text(answer_caption)
        
        # Load and preprocess image
        image = Image.open(guess_image_path).convert('RGB')
        inputs = self.processor(images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Tokenize captions
        text_inputs = self.processor(
            text=[answer_caption, f"NOT {answer_caption}"], 
            return_tensors="pt", 
            padding=True,
            truncation=True,
            max_length=MAX_SEQUENCE_LENGTH
        )
        text_inputs = {k: v.to(self.device) for k, v in text_inputs.items()}
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            text_features = self.model.get_text_features(**text_inputs)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=1, keepdim=True)
            text_features = text_features / text_features.norm(dim=1, keepdim=True)
            
            # Calculate similarity
            logits_per_image = image_features @ text_features.t()
            probs = logits_per_image.softmax(dim=-1)
            
        return probs[0][0].item()  # Return probability that guess image matches answer caption
    
    def img_similarity(self, image_path_1: str, image_path_2: str) -> float:
        # Load and preprocess images
        image1 = Image.open(image_path_1).convert('RGB')
        image2 = Image.open(image_path_2).convert('RGB')
        
        inputs1 = self.processor(images=image1, return_tensors="pt", padding=True)
        inputs2 = self.processor(images=image2, return_tensors="pt", padding=True)
        
        inputs1 = {k: v.to(self.device) for k, v in inputs1.items()}
        inputs2 = {k: v.to(self.device) for k, v in inputs2.items()}
        
        # Get image embeddings
        with torch.no_grad():
            emb1 = self.model.get_image_features(**inputs1)
            emb2 = self.model.get_image_features(**inputs2)
            
            # Normalize embeddings
            emb1 = emb1 / emb1.norm(dim=1, keepdim=True)
            emb2 = emb2 / emb2.norm(dim=1, keepdim=True)
            
            # Calculate cosine similarity
            similarity = (emb1 @ emb2.t()).item()
            
        return similarity

    def caption_similarity(self, cap_1: str, cap_2: str) -> float:
        # Truncate captions if needed
        cap_1 = self._truncate_text(cap_1)
        cap_2 = self._truncate_text(cap_2)
        
        # Tokenize captions
        inputs = self.processor(
            text=[cap_1, cap_2], 
            return_tensors="pt", 
            padding=True,
            truncation=True,
            max_length=MAX_SEQUENCE_LENGTH
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get text embeddings
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)
            features = features / features.norm(dim=1, keepdim=True)
            
            # Calculate cosine similarity
            similarity = (features[0] @ features[1].t()).item()
            
        return similarity

    def metric_similarity(self, img_similarity: float, caption_similarity: float, beta: float = 0.5) -> float:
        return beta * img_similarity + (1 - beta) * caption_similarity

    def decision_threshold(self, object_match: float, metric: float) -> bool:
        return object_match > 0.80 or metric > 0.80
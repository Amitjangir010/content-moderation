from transformers import pipeline
from PIL import Image
import io

class ImageModerator:
    def __init__(self):
        self.classifier = pipeline(
            "image-classification",
            model="Falconsai/nsfw_image_detection",
            top_k=3
        )
    
    def check_image(self, file_content: bytes):
        image = Image.open(io.BytesIO(file_content))
        
        # Get predictions
        results = self.classifier(image)
        
        # Get NSFW probability
        nsfw_score = next(
            (pred['score'] for pred in results if pred['label'].lower() == 'nsfw'),
            0.0
        )
        
        return {
            "status": "NSFW Image" if nsfw_score > 0.5 else "Safe Image",
            "confidence": nsfw_score,
            "predictions": results
        } 
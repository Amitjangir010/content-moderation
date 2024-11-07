from transformers import pipeline

class TextModerator:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            return_all_scores=True
        )
    
    def check_content(self, text: str):
        results = self.classifier(text)[0]
        
        # Get toxic score and normalize it between 0 and 1
        toxic_score = min(1.0, sum(score['score'] for score in results if 'toxic' in score['label'].lower()))
        
        return {
            "status": "Toxic Text" if toxic_score > 0.5 else "Safe Text",
            "confidence": toxic_score  # Now will always be between 0 and 1
        } 
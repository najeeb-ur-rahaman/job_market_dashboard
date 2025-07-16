from transformers import pipeline
from skills import SKILLS

class SkillExtractor:
    def __init__(self):
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0  # use 0 for GPU or -1 for CPU
        )
    
    def extract(self, text, top_k=5):
        if not text or not text.strip():
            raise ValueError("Input text is empty. Please provide valid input.")
        
        result = self.classifier(
            text,
            candidate_labels = SKILLS,
            multi_label = True,
            truncation = True

        )

        return result['labels'][:top_k]
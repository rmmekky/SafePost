import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class TextClassifier:
    def __init__(self):
        # جاهز للاستخدام بدون Fine-tuning
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        # إزالة .to(device) لتجنب مشاكل meta tensors
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased-finetuned-sst-2-english"
        )

    def classify(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()
        # 1 = Positive (Safe), 0 = Negative (Inappropriate)
        return "Safe to post" if pred == 1 else "Inappropriate content"

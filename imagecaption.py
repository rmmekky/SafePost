from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

class ImageCaptioning:
    def __init__(self):
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        # إزالة .to(device) لتجنب مشاكل meta tensors
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def generate_caption(self, image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(image, return_tensors="pt")
        out = self.model.generate(**inputs)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption

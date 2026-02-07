from transformers import BlipForConditionalGeneration, BlipProcessor
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

class Captioner:
    def __init__(self, model_id="Salesforce/blip-image-captioning-base"):
        self.processor = BlipProcessor.from_pretrained(model_id)
        self.model = BlipForConditionalGeneration.from_pretrained(model_id)

    def caption(self, img_bgr):
        img_rgb = Image.fromarray(img_bgr[:, :, ::-1])  # BGR->RGB
        inputs = self.processor(images=img_rgb, return_tensors="pt")
        out_ids = self.model.generate(**inputs, max_new_tokens=30)
        return self.processor.batch_decode(out_ids, skip_special_tokens=True)[0]

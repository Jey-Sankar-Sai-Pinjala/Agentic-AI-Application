import pytesseract
from PIL import Image
from typing import Dict, Any, Optional


class OCRTool:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            
            try:
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
            except:
                avg_confidence = 0.5
            
            return {
                "text": extracted_text.strip(),
                "confidence": avg_confidence,
                "metadata": {
                    "method": "pytesseract",
                    "image_size": img.size
                },
                "success": True
            }
        except Exception as e:
            return {
                "text": None,
                "confidence": 0.0,
                "error": str(e),
                "success": False,
                "metadata": {}
            }

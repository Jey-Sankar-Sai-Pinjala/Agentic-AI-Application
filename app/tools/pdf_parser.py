import pdfplumber
from typing import Dict, Any


class PDFParserTool:
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str, use_ocr_fallback: bool = True) -> Dict[str, Any]:
        try:
            text_parts = []
            total_pages = 0
            pages_with_text = 0
            
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
                        pages_with_text += 1
            
            extracted_text = "\n\n".join(text_parts)
            confidence = pages_with_text / total_pages if total_pages > 0 else 0.0
            
            fallback_used = False
            if (not extracted_text or confidence < 0.5) and use_ocr_fallback:
                try:
                    from .ocr import OCRTool
                    ocr_tool = OCRTool()
                    ocr_result = ocr_tool.extract_text_from_image(pdf_path)
                    if ocr_result.get("success") and ocr_result.get("text"):
                        extracted_text = ocr_result["text"]
                        confidence = ocr_result.get("confidence", 0.5)
                        fallback_used = True
                except Exception:
                    pass
            
            return {
                "text": extracted_text,
                "confidence": confidence,
                "metadata": {
                    "total_pages": total_pages,
                    "pages_with_text": pages_with_text,
                    "method": "ocr_fallback" if fallback_used else "pdfplumber"
                },
                "fallback_used": fallback_used,
                "success": True
            }
        except Exception as e:
            return {
                "text": None,
                "confidence": 0.0,
                "error": str(e),
                "success": False,
                "fallback_used": False,
                "metadata": {}
            }

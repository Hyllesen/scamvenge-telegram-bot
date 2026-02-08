"""
Image processor module for OCR and store name extraction.

This module is pure logic with no network/Telegram dependencies for testability.
"""
import re
from typing import List, Tuple, Optional
import easyocr
from PIL import Image
from .exceptions import InvalidImageError, OCRError


class ImageProcessor:
    """Handles OCR processing and store name extraction from screenshots."""
    
    # Keywords that indicate a valid "Store Follow" screenshot
    VALIDATION_KEYWORDS = ["Following", "Sold", "Items"]
    
    # UI keywords to exclude when finding store name
    UI_KEYWORDS = ["Following", "Sold", "Items", "Follow", "Message", "Share", "More"]
    
    # Crop to top N% of image to focus on header (where store name is)
    CROP_TOP_PERCENT = 25  # Only process top 25% of image
    
    def __init__(self, languages: List[str] = None, gpu: bool = False, crop_top: bool = True):
        """
        Initialize the OCR reader.
        
        Args:
            languages: List of language codes for OCR (default: ['en'])
            gpu: Whether to use GPU acceleration (default: False)
            crop_top: Whether to crop to top portion of image (default: True)
        """
        if languages is None:
            languages = ['en']
        
        self.crop_top = crop_top
        
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu)
        except Exception as e:
            raise OCRError(f"Failed to initialize EasyOCR reader: {e}")
    
    def _crop_image(self, image_path: str) -> str:
        """
        Crop image to top portion to focus on header/store name.
        
        Args:
            image_path: Path to original image
            
        Returns:
            Path to cropped image (temporary file)
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            # Crop to top N% of image
            crop_height = int(height * (self.CROP_TOP_PERCENT / 100))
            cropped = img.crop((0, 0, width, crop_height))
            
            # Save to temporary file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            cropped.save(temp_file.name)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            raise OCRError(f"Failed to crop image: {e}")
    
    def validate_keywords(self, ocr_results: List[Tuple]) -> bool:
        """
        Validate that the OCR results contain at least one required keyword.
        
        Args:
            ocr_results: List of OCR results from EasyOCR
                Each result is a tuple: (bbox, text, confidence)
        
        Returns:
            True if valid keywords found
            
        Raises:
            InvalidImageError: If no valid keywords found
        """
        # Extract all text from OCR results
        all_text = " ".join([result[1] for result in ocr_results])
        
        # Check for keywords (case-insensitive)
        all_text_lower = all_text.lower()
        found_keywords = [kw for kw in self.VALIDATION_KEYWORDS 
                         if kw.lower() in all_text_lower]
        
        if not found_keywords:
            raise InvalidImageError(
                f"Image does not contain required keywords: {self.VALIDATION_KEYWORDS}"
            )
        
        return True
    
    def extract_store_name(self, ocr_results: List[Tuple]) -> str:
        """
        Extract the store name using font size heuristic.
        
        The store name is assumed to be the text element with the largest
        font size (bounding box height) that is not a UI keyword.
        
        Args:
            ocr_results: List of OCR results from EasyOCR
                Each result is a tuple: (bbox, text, confidence)
        
        Returns:
            Cleaned store name
            
        Raises:
            InvalidImageError: If no valid store name found
        """
        if not ocr_results:
            raise InvalidImageError("No text found in image")
        
        # Calculate height for each text element and filter UI keywords
        candidates = []
        for bbox, text, confidence in ocr_results:
            # Skip empty or very short text
            text_clean = text.strip()
            if len(text_clean) < 2:
                continue
            
            # Skip UI keywords
            if text_clean in self.UI_KEYWORDS:
                continue
            
            # Calculate bounding box height (bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]])
            heights = [bbox[2][1] - bbox[0][1], bbox[3][1] - bbox[1][1]]
            avg_height = sum(heights) / len(heights)
            
            candidates.append({
                'text': text_clean,
                'height': avg_height,
                'confidence': confidence
            })
        
        if not candidates:
            raise InvalidImageError("No valid store name candidates found")
        
        # Sort by height (descending) to get largest text
        candidates.sort(key=lambda x: x['height'], reverse=True)
        
        # Return the largest text element
        store_name = candidates[0]['text']
        return self.normalize_text(store_name)
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for consistent storage and comparison.
        
        Args:
            text: Raw text string
            
        Returns:
            Normalized text (cleaned, trimmed)
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def process_image(self, image_path: str) -> str:
        """
        Main entry point: Process an image and extract store name.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted store name
            
        Raises:
            InvalidImageError: If image is invalid or no keywords found
            OCRError: If OCR processing fails
        """
        cropped_path = None
        try:
            # Crop to top portion if enabled
            if self.crop_top:
                cropped_path = self._crop_image(image_path)
                ocr_path = cropped_path
            else:
                ocr_path = image_path
            
            # Run OCR
            ocr_results = self.reader.readtext(ocr_path)
            
            if not ocr_results:
                raise InvalidImageError("No text detected in image")
            
            # Validate keywords
            self.validate_keywords(ocr_results)
            
            # Extract store name
            store_name = self.extract_store_name(ocr_results)
            
            return store_name
            
        except InvalidImageError:
            raise
        except Exception as e:
            raise OCRError(f"OCR processing failed: {e}")
        finally:
            # Cleanup temporary cropped file
            if cropped_path:
                try:
                    import os
                    os.unlink(cropped_path)
                except:
                    pass

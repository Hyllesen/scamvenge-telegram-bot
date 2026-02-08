"""
Unit tests for the processor module with mocked OCR results.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.processor import ImageProcessor
from src.exceptions import InvalidImageError, OCRError


class TestImageProcessor(unittest.TestCase):
    """Test the ImageProcessor class with mocked data."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock EasyOCR to avoid loading the actual model
        with patch('src.processor.easyocr.Reader'):
            self.processor = ImageProcessor(languages=['en'], gpu=False)
    
    def test_validate_keywords_with_following(self):
        """Test validation with 'Following' keyword present."""
        ocr_results = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Nike Store", 0.95),
            ([[0, 60], [100, 60], [100, 90], [0, 90]], "Following", 0.98),
            ([[0, 100], [50, 100], [50, 120], [0, 120]], "1.2k", 0.92),
        ]
        
        # Should not raise exception
        result = self.processor.validate_keywords(ocr_results)
        self.assertTrue(result)
    
    def test_validate_keywords_with_sold(self):
        """Test validation with 'Sold' keyword present."""
        ocr_results = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Adidas Store", 0.95),
            ([[0, 60], [100, 60], [100, 90], [0, 90]], "Sold", 0.98),
        ]
        
        result = self.processor.validate_keywords(ocr_results)
        self.assertTrue(result)
    
    def test_validate_keywords_with_items(self):
        """Test validation with 'Items' keyword present."""
        ocr_results = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "The Shop", 0.95),
            ([[0, 60], [80, 60], [80, 90], [0, 90]], "Items", 0.98),
        ]
        
        result = self.processor.validate_keywords(ocr_results)
        self.assertTrue(result)
    
    def test_validate_keywords_case_insensitive(self):
        """Test that keyword validation is case-insensitive."""
        ocr_results = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Store ABC", 0.95),
            ([[0, 60], [100, 60], [100, 90], [0, 90]], "FOLLOWING", 0.98),
        ]
        
        result = self.processor.validate_keywords(ocr_results)
        self.assertTrue(result)
    
    def test_validate_keywords_no_keywords(self):
        """Test that validation fails when no keywords present."""
        ocr_results = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Some Store", 0.95),
            ([[0, 60], [100, 60], [100, 90], [0, 90]], "Random Text", 0.98),
        ]
        
        with self.assertRaises(InvalidImageError):
            self.processor.validate_keywords(ocr_results)
    
    def test_validate_keywords_empty_results(self):
        """Test validation with empty OCR results."""
        ocr_results = []
        
        with self.assertRaises(InvalidImageError):
            self.processor.validate_keywords(ocr_results)
    
    def test_extract_store_name_largest_font(self):
        """Test extraction based on largest font size."""
        ocr_results = [
            # Small text (height: 30)
            ([[0, 0], [50, 0], [50, 30], [0, 30]], "Following", 0.98),
            # Large text (height: 80) - Should be selected
            ([[0, 40], [200, 40], [200, 120], [0, 120]], "Nike Store", 0.95),
            # Medium text (height: 40)
            ([[0, 130], [100, 130], [100, 170], [0, 170]], "1.2k Sold", 0.92),
        ]
        
        store_name = self.processor.extract_store_name(ocr_results)
        self.assertEqual(store_name, "Nike Store")
    
    def test_extract_store_name_filters_ui_keywords(self):
        """Test that UI keywords are filtered out."""
        ocr_results = [
            # Large UI keyword (should be filtered)
            ([[0, 0], [200, 0], [200, 100], [0, 100]], "Following", 0.98),
            # Slightly smaller but valid store name
            ([[0, 110], [180, 110], [180, 200], [0, 200]], "Adidas Shop", 0.95),
        ]
        
        store_name = self.processor.extract_store_name(ocr_results)
        self.assertEqual(store_name, "Adidas Shop")
    
    def test_extract_store_name_multiple_large_texts(self):
        """Test extraction when multiple large texts exist."""
        ocr_results = [
            # First large text (height: 80)
            ([[0, 0], [200, 0], [200, 80], [0, 80]], "The Store", 0.95),
            # Second large text (height: 85) - Should be selected
            ([[0, 90], [220, 90], [220, 175], [0, 175]], "Best Shop", 0.96),
            # Smaller text
            ([[0, 180], [100, 180], [100, 210], [0, 210]], "Sold", 0.98),
        ]
        
        store_name = self.processor.extract_store_name(ocr_results)
        self.assertEqual(store_name, "Best Shop")
    
    def test_extract_store_name_empty_results(self):
        """Test extraction with empty OCR results."""
        ocr_results = []
        
        with self.assertRaises(InvalidImageError):
            self.processor.extract_store_name(ocr_results)
    
    def test_extract_store_name_only_ui_keywords(self):
        """Test extraction when only UI keywords present."""
        ocr_results = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Following", 0.98),
            ([[0, 60], [100, 60], [100, 110], [0, 110]], "Sold", 0.97),
            ([[0, 120], [100, 120], [100, 170], [0, 170]], "Items", 0.96),
        ]
        
        with self.assertRaises(InvalidImageError):
            self.processor.extract_store_name(ocr_results)
    
    def test_normalize_text_basic(self):
        """Test text normalization."""
        text = "  Nike   Store  "
        normalized = ImageProcessor.normalize_text(text)
        self.assertEqual(normalized, "Nike Store")
    
    def test_normalize_text_multiple_spaces(self):
        """Test normalization with multiple spaces."""
        text = "The    Big     Store"
        normalized = ImageProcessor.normalize_text(text)
        self.assertEqual(normalized, "The Big Store")
    
    def test_normalize_text_newlines(self):
        """Test normalization with newlines."""
        text = "Store\n\nName"
        normalized = ImageProcessor.normalize_text(text)
        self.assertEqual(normalized, "Store Name")
    
    @patch('src.processor.easyocr.Reader')
    def test_process_image_success(self, mock_reader_class):
        """Test full image processing pipeline."""
        # Mock OCR results
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 30], [0, 30]], "Following", 0.98),
            ([[0, 40], [200, 40], [200, 120], [0, 120]], "Test Store", 0.95),
        ]
        mock_reader_class.return_value = mock_reader
        
        # Disable cropping for mock tests
        processor = ImageProcessor(languages=['en'], gpu=False, crop_top=False)
        store_name = processor.process_image("fake_path.jpg")
        
        self.assertEqual(store_name, "Test Store")
        mock_reader.readtext.assert_called_once_with("fake_path.jpg")
    
    @patch('src.processor.easyocr.Reader')
    def test_process_image_no_text(self, mock_reader_class):
        """Test processing image with no text detected."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = []
        mock_reader_class.return_value = mock_reader
        
        # Disable cropping for mock tests
        processor = ImageProcessor(languages=['en'], gpu=False, crop_top=False)
        
        with self.assertRaises(InvalidImageError):
            processor.process_image("fake_path.jpg")
    
    @patch('src.processor.easyocr.Reader')
    def test_process_image_no_keywords(self, mock_reader_class):
        """Test processing image without required keywords."""
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Random Store", 0.95),
            ([[0, 60], [100, 60], [100, 90], [0, 90]], "Some Text", 0.90),
        ]
        mock_reader_class.return_value = mock_reader
        
        # Disable cropping for mock tests
        processor = ImageProcessor(languages=['en'], gpu=False, crop_top=False)
        
        with self.assertRaises(InvalidImageError):
            processor.process_image("fake_path.jpg")
    
    @patch('src.processor.easyocr.Reader')
    def test_process_image_ocr_failure(self, mock_reader_class):
        """Test handling of OCR failures."""
        mock_reader = MagicMock()
        mock_reader.readtext.side_effect = Exception("OCR failed")
        mock_reader_class.return_value = mock_reader
        
        processor = ImageProcessor(languages=['en'], gpu=False)
        
        with self.assertRaises(OCRError):
            processor.process_image("fake_path.jpg")


if __name__ == '__main__':
    unittest.main()

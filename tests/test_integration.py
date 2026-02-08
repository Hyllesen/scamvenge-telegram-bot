"""
Integration tests for real OCR processing on fixture images.
"""
import unittest
import os
from pathlib import Path
from src.processor import ImageProcessor
from src.exceptions import InvalidImageError


# Expected results mapping: filename -> expected store name
# UPDATE THIS when adding new fixture images
EXPECTED_RESULTS = {
    'QYIQ_items.jpg': 'QYIQ',
    'alien_artificial_flow_following.jpg': 'alien artificial flow',
    'zhi_heng_following.jpg': 'zhi heng',
    # Add your fixtures here
}


class TestIntegration(unittest.TestCase):
    """Integration tests with real OCR on fixture images."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures."""
        cls.fixtures_dir = Path(__file__).parent / 'fixtures'
        
        # Check if fixtures directory exists and has images
        if not cls.fixtures_dir.exists():
            cls.skip_tests = True
            return
        
        # Get list of image files
        cls.image_files = list(cls.fixtures_dir.glob('*.jpg')) + \
                         list(cls.fixtures_dir.glob('*.png')) + \
                         list(cls.fixtures_dir.glob('*.jpeg'))
        
        # Skip tests if no images found
        cls.skip_tests = len(cls.image_files) == 0
        
        if not cls.skip_tests:
            # Initialize processor (this will load the EasyOCR model)
            print("\nInitializing EasyOCR (this may take a moment)...")
            cls.processor = ImageProcessor(languages=['en'], gpu=False)
            print("EasyOCR initialized successfully")
    
    def setUp(self):
        """Set up each test."""
        if self.__class__.skip_tests:
            self.skipTest("No fixture images found in tests/fixtures/")
    
    def test_fixture_discovery(self):
        """Test that fixture images can be discovered."""
        self.assertGreater(len(self.image_files), 0, 
                          "No fixture images found. Add images to tests/fixtures/")
        print(f"\nFound {len(self.image_files)} fixture image(s)")
    
    def test_ocr_on_all_fixtures(self):
        """Test OCR processing on all fixture images."""
        results = {}
        
        for image_path in self.image_files:
            filename = image_path.name
            print(f"\nProcessing: {filename}")
            
            try:
                # Run actual OCR
                store_name = self.processor.process_image(str(image_path))
                results[filename] = {
                    'status': 'success',
                    'store_name': store_name
                }
                print(f"  ✓ Extracted: '{store_name}'")
                
                # Check against expected results if defined
                if filename in EXPECTED_RESULTS:
                    expected = EXPECTED_RESULTS[filename]
                    self.assertEqual(store_name, expected,
                                   f"Extracted '{store_name}' but expected '{expected}'")
                    print(f"  ✓ Matches expected: '{expected}'")
                else:
                    print(f"  ⚠ No expected result defined (add to EXPECTED_RESULTS)")
                    
            except InvalidImageError as e:
                results[filename] = {
                    'status': 'invalid',
                    'error': str(e)
                }
                print(f"  ✗ Invalid image: {e}")
                self.fail(f"Image should be valid: {filename}")
                
            except Exception as e:
                results[filename] = {
                    'status': 'error',
                    'error': str(e)
                }
                print(f"  ✗ Error: {e}")
                raise
        
        # Print summary
        print("\n" + "="*60)
        print("INTEGRATION TEST SUMMARY")
        print("="*60)
        for filename, result in results.items():
            if result['status'] == 'success':
                print(f"✓ {filename}: {result['store_name']}")
            else:
                print(f"✗ {filename}: {result['status']} - {result.get('error', 'Unknown')}")
        print("="*60)
    
    def test_ocr_performance(self):
        """Test OCR processing time (benchmark)."""
        import time
        
        if not self.image_files:
            self.skipTest("No fixture images for performance test")
        
        # Test on first image only
        image_path = self.image_files[0]
        
        start_time = time.time()
        store_name = self.processor.process_image(str(image_path))
        elapsed_time = time.time() - start_time
        
        print(f"\nOCR Performance:")
        print(f"  Image: {image_path.name}")
        print(f"  Time: {elapsed_time:.2f} seconds")
        print(f"  Result: '{store_name}'")
        
        # Performance assertion (should complete within 30 seconds on CPU)
        self.assertLess(elapsed_time, 30.0,
                       "OCR took too long (>30s). Consider using GPU acceleration.")


if __name__ == '__main__':
    unittest.main(verbosity=2)

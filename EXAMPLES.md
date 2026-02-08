# Example Usage & Testing Guide

## Example 1: Testing the Processor (Without Running Bot)

```python
from src.processor import ImageProcessor

# Initialize processor
processor = ImageProcessor(languages=['en'], gpu=False)

# Process an image
try:
    store_name = processor.process_image('path/to/screenshot.jpg')
    print(f"Extracted store name: {store_name}")
except InvalidImageError as e:
    print(f"Invalid image: {e}")
```

## Example 2: Testing Database Operations

```python
from src.database import StoreDatabase

# Initialize database
db = StoreDatabase('./test.db')

# Add a store
db.add_store('Nike Store', original_message_id=12345)

# Check for duplicates
is_dup, matched = db.is_duplicate('Nike Store')
print(f"Is duplicate: {is_dup}, Matched: {matched}")

# Check fuzzy match
is_dup, matched = db.is_duplicate('nike stor')  # Missing 'e'
print(f"Fuzzy match: {is_dup}, Matched: {matched}")

# Get stats
stats = db.get_stats()
print(f"Total stores: {stats['total_stores']}")

db.close()
```

## Example 3: Running Tests

### Run all tests:
```bash
pytest -v
```

### Run specific test file:
```bash
pytest tests/test_processor.py -v
```

### Run specific test:
```bash
pytest tests/test_processor.py::TestImageProcessor::test_extract_store_name_largest_font -v
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=term-missing
```

### Run only fast tests (skip integration):
```bash
pytest -v -m "not integration"
```

## Example 4: Bot Configuration

### Minimal .env configuration:
```env
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+1234567890
SOURCE_GROUP=Alloy
TARGET_USER=Imelda
DATABASE_PATH=./data/stores.db
TEST_MODE=false
LOG_LEVEL=INFO
```

### Running in test mode (dry run):
```bash
# Method 1: Set in .env
TEST_MODE=true python main.py

# Method 2: Environment variable
TEST_MODE=true LOG_LEVEL=DEBUG python main.py

# Method 3: Edit .env file directly
# Change: TEST_MODE=false → TEST_MODE=true
python main.py
```

### Test mode output example:
```
2026-02-08 15:00:00 - INFO - Logged in as: John (+1234567890)
2026-02-08 15:00:00 - WARNING - ============================================================
2026-02-08 15:00:00 - WARNING - 🧪 TEST MODE ENABLED - Messages will NOT be forwarded
2026-02-08 15:00:00 - WARNING -    Database will NOT be modified
2026-02-08 15:00:00 - WARNING - ============================================================
2026-02-08 15:00:05 - INFO - New photo message received (ID: 12345)
2026-02-08 15:00:05 - INFO - Running OCR on image...
2026-02-08 15:00:08 - INFO - Extracted store name: 'Nike Store'
2026-02-08 15:00:08 - INFO - ============================================================
2026-02-08 15:00:08 - INFO - 🧪 TEST MODE: Would forward to 'Imelda'
2026-02-08 15:00:08 - INFO -    Store Name: 'Nike Store'
2026-02-08 15:00:08 - INFO -    Original Message ID: 12345
2026-02-08 15:00:08 - INFO -    Would save to database: ./data/stores.db
2026-02-08 15:00:08 - INFO -    ✅ UNIQUE - Would be forwarded in production mode
2026-02-08 15:00:08 - INFO - ============================================================
```

### Running with debug logging:
```bash
LOG_LEVEL=DEBUG python main.py
```

## Example 5: Simulating OCR Results for Testing

```python
# Mock OCR results (for testing without actual images)
mock_ocr_results = [
    # Format: (bbox, text, confidence)
    ([[0, 0], [100, 0], [100, 30], [0, 30]], "Following", 0.98),
    ([[0, 40], [200, 40], [200, 120], [0, 120]], "Nike Store", 0.95),
    ([[0, 130], [100, 130], [100, 160], [0, 160]], "1.2k Sold", 0.92),
]

processor = ImageProcessor()
store_name = processor.extract_store_name(mock_ocr_results)
print(store_name)  # Output: "Nike Store"
```

## Example 6: Adding Integration Test Fixtures

1. **Add sample image:**
   ```bash
   cp my_screenshot.jpg tests/fixtures/nike_following.jpg
   ```

2. **Update expected results in `tests/test_integration.py`:**
   ```python
   EXPECTED_RESULTS = {
       'nike_following.jpg': 'Nike Store',
       'adidas_sold.jpg': 'Adidas',
   }
   ```

3. **Run integration tests:**
   ```bash
   pytest tests/test_integration.py -v -s
   ```

## Example 7: Manual Testing Workflow

1. **Test processor standalone:**
   ```bash
   python3 << EOF
   from src.processor import ImageProcessor
   processor = ImageProcessor(languages=['en'], gpu=False)
   result = processor.process_image('tests/fixtures/sample.jpg')
   print(f"Result: {result}")
   EOF
   ```

2. **Test database operations:**
   ```bash
   python3 << EOF
   from src.database import StoreDatabase
   db = StoreDatabase('./test.db')
   db.add_store('Test Store')
   print(db.is_duplicate('Test Store'))
   db.close()
   EOF
   ```

## Example 8: Debugging Failed OCR

When OCR fails, check the logs:

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py

# Look for:
# - "Running OCR on image..." - Image download succeeded
# - "Extracted store name: ..." - OCR succeeded
# - "Invalid image (no keywords): ..." - Image validation failed
# - "OCR failed: ..." - OCR processing error
```

## Example 9: Testing Fuzzy Matching Threshold

```python
from src.database import StoreDatabase

db = StoreDatabase('./test.db')
db.add_store('Nike Store')

# Test various similarities
test_cases = [
    'Nike Store',      # 100% match
    'nike store',      # Case difference
    'Nike Stor',       # 1 char missing
    'NikeStore',       # No space
    'Nike  Store',     # Extra space
    'Adidas',          # Completely different
]

for test in test_cases:
    is_dup, matched = db.is_duplicate(test)
    print(f"'{test}': {'DUPLICATE' if is_dup else 'UNIQUE'}")

db.close()
```

## Example 10: Running Bot in Development Mode

```bash
# Terminal 1: Run bot with debug logging
LOG_LEVEL=DEBUG python main.py

# Terminal 2: Monitor logs
tail -f bot.log  # If logging to file

# Or use tmux/screen for persistent session
tmux new -s telegram-bot
python main.py
# Ctrl+B, D to detach
```

## Common Test Commands

```bash
# Quick validation (no installation needed for these tests)
pytest tests/test_processor.py tests/test_database.py -v

# Full test suite
pytest -v

# Test with output
pytest -v -s

# Test specific pattern
pytest -k "test_extract" -v

# Stop on first failure
pytest -x

# Show slowest tests
pytest --durations=10
```

## Troubleshooting Tests

**Issue**: `ModuleNotFoundError: No module named 'src'`
```bash
# Solution: Activate venv
source venv/bin/activate
```

**Issue**: `ImportError: cannot import name 'ImageProcessor'`
```bash
# Solution: Check PYTHONPATH or run from project root
cd /Users/stefan/scamvenge-telegram-bot
pytest -v
```

**Issue**: Tests are very slow
```bash
# Solution: Skip integration tests
pytest tests/test_processor.py tests/test_database.py -v
```

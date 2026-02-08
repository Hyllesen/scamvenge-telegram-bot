# Telegram Store Follow Bot

A modular Python bot that automates monitoring a Telegram group for "Store Follow" screenshots, extracts store names via OCR, and forwards unique entries.

## Features

- 🤖 Automated Telegram group monitoring
- 🔍 OCR-based text extraction using EasyOCR
- ✅ Keyword validation for "Store Follow" screenshots
- 📊 Font size heuristic for store name extraction
- 🔄 Fuzzy duplicate detection (~90% similarity)
- 💾 SQLite database for tracking processed stores
- 🧪 Comprehensive test suite (unit + integration)

## Architecture

The project uses a **two-module design** for testability:

- **`processor.py`**: Pure logic module (OCR, validation, extraction) - no network code
- **`bot.py`**: Telegram integration (auth, messaging, database, forwarding)

## Requirements

- Python 3.10+
- Telegram API credentials (from https://my.telegram.org)
- (Optional) GPU for faster OCR processing

## Installation

### Option 1: Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd scamvenge-telegram-bot
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your Telegram API credentials
```

### Option 2: Docker Installation (Recommended)

**Prerequisites:** Docker and Docker Compose installed

1. **Clone the repository**
```bash
git clone <repository-url>
cd scamvenge-telegram-bot
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your Telegram API credentials
```

3. **Build and run**
```bash
# Using helper script (recommended)
./docker-helper.sh build
./docker-helper.sh start

# Or using docker-compose directly
docker-compose up -d
```

**Docker benefits:**
- ✅ No Python/dependency setup needed
- ✅ Consistent environment across systems
- ✅ Easy deployment and scaling
- ✅ Automatic restarts
- ✅ Resource limits and monitoring

## Configuration

### Getting Telegram API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy `api_id` and `api_hash` to your `.env` file

### Environment Variables

Edit `.env` with your settings:

```env
API_ID=12345678                    # Your Telegram API ID
API_HASH=abcdef1234567890...       # Your Telegram API Hash
PHONE_NUMBER=+1234567890           # Your phone number (with country code)

SOURCE_GROUP=Alloy                 # Group to monitor
TARGET_USER=Imelda                 # User to forward messages to

DATABASE_PATH=./data/stores.db     # SQLite database path
TEST_MODE=false                    # Set to 'true' for dry run (no forwarding)
LOG_LEVEL=INFO                     # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Test Mode

Use test mode to verify the bot works without sending real messages:

```bash
# Set in .env file
TEST_MODE=true

# Or run directly
TEST_MODE=true python main.py
```

**Test mode behavior:**
- Processes all images normally
- Runs OCR and extraction
- Checks for duplicates
- **Does NOT forward messages**
- **Does NOT modify database**
- Logs all actions as if in production

Perfect for:
- Testing bot setup
- Verifying OCR accuracy
- Testing without spamming Imelda
- Development and debugging

## Usage

### Local Installation

**Production mode (forwards messages):**
```bash
python main.py
```

**Test mode (dry run, no forwarding):**
```bash
TEST_MODE=true python main.py
# or set TEST_MODE=true in .env
```

### Docker Installation

**Using helper script (recommended):**
```bash
./docker-helper.sh start    # Start in background
./docker-helper.sh logs     # View logs
./docker-helper.sh test     # Run in test mode
./docker-helper.sh stop     # Stop bot
```

**Using docker-compose:**
```bash
docker-compose up -d        # Start in background
docker-compose logs -f      # View logs
docker-compose down         # Stop bot
```

**Test mode with Docker:**
```bash
docker-compose run --rm -e TEST_MODE=true telegram-bot
```

In test mode:
- ✅ Processes images and extracts store names
- ✅ Checks for duplicates
- ❌ Does NOT forward messages to Imelda
- ❌ Does NOT modify the database
- 📝 Logs what would happen in production

On first run, you'll be prompted for:
1. Phone verification code (sent via Telegram)
2. 2FA password (if enabled)

The bot will then run continuously, monitoring the specified group.

### Running Tests

**Local installation:**
```bash
pytest -v                    # All tests
pytest tests/test_processor.py -v    # Processor tests only
pytest tests/test_database.py -v     # Database tests only
```

**Docker installation:**
```bash
./docker-helper.sh run-tests
# or
docker-compose run --rm telegram-bot pytest -v
```

**All tests:**
```bash
pytest -v
```

## Project Structure

```
scamvenge-telegram-bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Telegram integration
│   ├── processor.py        # OCR & extraction logic
│   ├── database.py         # SQLite operations
│   └── exceptions.py       # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_processor.py   # Unit tests (mocked)
│   ├── test_database.py    # Database tests
│   ├── test_integration.py # Real OCR tests
│   └── fixtures/           # Sample images for testing
├── data/                   # Database storage (created on first run)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore
├── README.md
└── main.py                # Entry point
```

## How It Works

1. **Monitoring**: Bot listens to the "Alloy" group for photo messages
2. **Download**: Photos are downloaded to a temporary location
3. **OCR**: EasyOCR extracts text from the image
4. **Validation**: Checks for keywords ("Following", "Sold", "Items")
5. **Extraction**: Identifies store name (largest text element, excluding UI keywords)
6. **Duplicate Check**: Fuzzy matching against database (~90% similarity)
7. **Forward**: If unique, forwards to "Imelda" and saves to database
8. **Cleanup**: Temporary files are removed

## OCR Accuracy

- **CPU Mode**: Slower but works on all systems
- **GPU Mode**: Much faster (requires CUDA)
- **Supported Formats**: PNG, JPG, JPEG
- **Expected Accuracy**: >80% on clear screenshots

## Fuzzy Matching

The bot uses fuzzy string matching (90% threshold) to handle:
- Minor typos in OCR
- Spacing variations ("Store ABC" vs "StoreABC")
- Special character differences

Adjust the threshold in `src/database.py` if needed.

## Troubleshooting

**Local Installation:**

**Issue**: Bot doesn't start
- Check `.env` credentials are correct
- Ensure phone number includes country code (+1...)

**Issue**: OCR is very slow
- EasyOCR is CPU-bound by default
- Consider GPU setup for production use

**Issue**: Too many/few duplicates detected
- Adjust fuzzy match threshold in `src/database.py`
- Default is 90% (range: 0-100)

**Issue**: Rate limit errors
- Telegram has built-in rate limits
- Bot handles `FloodWaitError` automatically

**Docker Installation:**

**Issue**: Container fails to start
- Check `.env` file exists and has valid credentials
- Check logs: `docker-compose logs`

**Issue**: Database not persisting
- Ensure `./data` directory exists and has correct permissions
- Check volume mounts in `docker-compose.yml`

**Issue**: Session files not persisting
- Session files are mounted as volumes in docker-compose.yml
- Don't delete `bot_session.session` files while container is running

**Issue**: Out of memory
- Adjust resource limits in `docker-compose.yml`
- EasyOCR requires ~1-2GB RAM minimum

**Issue**: Cannot connect to Telegram
- Check firewall settings
- Ensure container has internet access

## Testing Notes

### Adding Test Fixtures

To test with real images:

1. Place "Store Follow" screenshots in `tests/fixtures/`
2. Name files descriptively (e.g., `store_nike_follow.jpg`)
3. Update `tests/test_integration.py` with expected store names
4. Run integration tests

The integration test suite will:
- Discover all images in `fixtures/`
- Run actual OCR
- Verify extracted store names match expectations

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open a GitHub issue.

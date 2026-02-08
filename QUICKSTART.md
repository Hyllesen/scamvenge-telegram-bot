# Quick Start Guide

## Choose Your Installation Method

### Option A: Docker (Recommended) 🐳

**Pros:** No Python setup, consistent environment, easy deployment
**Cons:** Requires Docker

```bash
# 1. Install Docker (if needed)
# Visit: https://docs.docker.com/get-docker/

# 2. Clone and configure
git clone <repository-url>
cd scamvenge-telegram-bot
cp .env.example .env
# Edit .env with your Telegram credentials

# 3. Build image
./docker-helper.sh build

# 4. Authenticate (first time only)
./docker-helper.sh auth
# Enter the code you receive via Telegram

# 5. Start bot
./docker-helper.sh start

# 6. View logs
./docker-helper.sh logs

# Done! Bot is running in background
```

### Option B: Local Installation 🐍

**Pros:** Direct control, easier debugging
**Cons:** Requires Python 3.10+, manual dependency management

```bash
# 1. Clone repository
git clone <repository-url>
cd scamvenge-telegram-bot

# 2. Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with your Telegram credentials

# 5. Run bot
python main.py
```

## Getting Telegram API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy `api_id` and `api_hash` to `.env`

## Running the Bot

### Docker (Recommended)

```bash
# First time: authenticate
./docker-helper.sh auth

# Production mode
./docker-helper.sh start
./docker-helper.sh logs

# Test mode (dry run)
./docker-helper.sh test

# Stop
./docker-helper.sh stop

# Other commands
./docker-helper.sh --help
```

### Local Installation

```bash
# First time: authenticate
python authenticate.py

# Production mode
python main.py

# Test mode (dry run)
TEST_MODE=true python main.py
```

## Running Tests

### Docker

```bash
./docker-helper.sh run-tests
```

### Local

```bash
# Quick test (mocked, no OCR)
pytest tests/test_processor.py tests/test_database.py -v

# All tests
pytest -v
```

## Project Structure

```
src/
├── bot.py          - Telegram integration
├── processor.py    - OCR logic (pure, testable)
├── database.py     - SQLite with fuzzy matching
└── exceptions.py   - Custom exceptions

tests/
├── test_processor.py    - Unit tests (18 tests)
├── test_database.py     - Database tests (13 tests)
├── test_integration.py  - Real OCR tests (needs fixtures)
└── fixtures/           - Place sample images here
```

## Key Features

✅ Modular architecture (pure logic separated from Telegram)
✅ Fuzzy duplicate detection (90% threshold)
✅ Font size heuristic for store name extraction
✅ Comprehensive test suite (31 tests)
✅ Error handling and logging
✅ Automatic cleanup of temp files

## Testing with Real Images

1. Add sample "Store Follow" screenshots to `tests/fixtures/`
2. Update `EXPECTED_RESULTS` in `tests/test_integration.py`
3. Run: `pytest tests/test_integration.py -v`

## Troubleshooting

**"docker-compose: command not found"**: Script auto-detects v1/v2, use `./docker-helper.sh` commands
**"unable to open database file"**: You need to authenticate first with `./docker-helper.sh auth`
**"Please enter the code you received"**: Check your Telegram app for the auth code
**ModuleNotFoundError**: Activate venv first: `source venv/bin/activate`
**OCR slow**: EasyOCR uses CPU by default. Enable GPU for faster processing.
**Rate limits**: Bot handles `FloodWaitError` automatically.

## Next Steps

1. Configure `.env` with your Telegram credentials
2. Build: `./docker-helper.sh build`
3. Authenticate: `./docker-helper.sh auth` (first time only, check Telegram for code)
4. Start bot: `./docker-helper.sh start`
5. Add test fixtures for integration testing (optional)
6. Monitor logs for debugging: `./docker-helper.sh logs`

# Docker Deployment Guide

Complete guide for running the Telegram Store Follow Bot with Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2 (or v1 with `docker-compose` 1.29+)

Check versions:
```bash
docker --version
docker compose version  # Docker Compose v2
# OR
docker-compose --version  # Docker Compose v1
```

**Note:** The helper script automatically detects whether you have Docker Compose v2 (`docker compose`) or v1 (`docker-compose`) installed.

## Quick Start

1. **Clone and configure:**
```bash
git clone <repository-url>
cd scamvenge-telegram-bot
cp .env.example .env
# Edit .env with your credentials
```

2. **Build and start:**
```bash
./docker-helper.sh build
./docker-helper.sh start
```

3. **View logs:**
```bash
./docker-helper.sh logs
```

## Docker Helper Script

The `docker-helper.sh` script simplifies common operations:

```bash
./docker-helper.sh [command]

Commands:
  build       - Build the Docker image
  start       - Start bot in background
  run         - Start bot with live logs
  stop        - Stop the bot
  restart     - Restart the bot
  logs        - View logs (live)
  test        - Run in test mode
  run-tests   - Run test suite
  shell       - Open shell in container
  status      - Show status and resources
  clean       - Remove everything
```

## Manual Docker Commands

### Build Image
```bash
docker-compose build
```

### Start Bot (Background)
```bash
docker-compose up -d
```

### Start Bot (Foreground with Logs)
```bash
docker-compose up
```

### View Logs
```bash
docker-compose logs -f
docker-compose logs -f --tail=100  # Last 100 lines
```

### Stop Bot
```bash
docker-compose down
```

### Restart Bot
```bash
docker-compose restart
```

## Test Mode

Run bot in test mode (no forwarding, no database writes):

```bash
# Using helper
./docker-helper.sh test

# Using docker-compose
docker-compose run --rm -e TEST_MODE=true telegram-bot
```

## Running Tests

```bash
# Using helper
./docker-helper.sh run-tests

# Using docker-compose
docker-compose run --rm telegram-bot pytest -v
```

## Volume Mounts

Docker Compose automatically mounts:

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./data` | `/app/data` | Database persistence |
| `./bot_session.session` | `/app/bot_session.session` | Telegram session |
| `./tests/fixtures` | `/app/tests/fixtures` | Test images |
| `./logs` | `/app/logs` | Log files (optional) |

## First Run (Phone Verification)

On first run, you'll need to verify your phone:

```bash
# Start in foreground to see verification prompt
docker-compose up

# You'll see:
# "Please enter the code you received: "
# Enter the code from Telegram
```

After verification, the session file is saved and future runs won't require verification.

## Environment Variables

Configure via `.env` file:

```env
API_ID=12345678
API_HASH=your_hash
PHONE_NUMBER=+1234567890
SOURCE_GROUP=Alloy
TARGET_USER=Imelda
DATABASE_PATH=/app/data/stores.db
TEST_MODE=false
LOG_LEVEL=INFO
```

**Note:** Paths in `.env` should use container paths (e.g., `/app/data/stores.db`)

## Resource Limits

Edit `docker-compose.yml` to set limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

## Monitoring

### Container Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats telegram-store-bot
```

### Health Check
```bash
docker inspect --format='{{.State.Health.Status}}' telegram-store-bot
```

## Logs

### View Live Logs
```bash
docker-compose logs -f
```

### View Last N Lines
```bash
docker-compose logs --tail=50
```

### Save Logs to File
```bash
docker-compose logs > bot-logs.txt
```

### Log Rotation

Docker automatically rotates logs (configured in docker-compose.yml):
- Max size: 10MB per file
- Max files: 3
- Total: ~30MB max

## Debugging

### Shell Access
```bash
# Using helper
./docker-helper.sh shell

# Using docker-compose
docker-compose exec telegram-bot /bin/bash
```

### Check Files
```bash
docker-compose exec telegram-bot ls -la /app/data
docker-compose exec telegram-bot ls -la /app/*.session
```

### Check Processes
```bash
docker-compose exec telegram-bot ps aux
```

### View Environment
```bash
docker-compose exec telegram-bot env | grep -E 'API|TEST|LOG'
```

## Backup and Restore

### Backup Database
```bash
# Database is in ./data directory
cp ./data/stores.db ./data/stores.db.backup
```

### Backup Session
```bash
cp bot_session.session bot_session.session.backup
```

### Restore
```bash
cp ./data/stores.db.backup ./data/stores.db
cp bot_session.session.backup bot_session.session
docker-compose restart
```

## Updating

### Update Code
```bash
git pull
./docker-helper.sh stop
./docker-helper.sh build
./docker-helper.sh start
```

### Update Dependencies
```bash
# Edit requirements.txt
./docker-helper.sh stop
./docker-helper.sh build
./docker-helper.sh start
```

## Production Deployment

### Recommended Setup

1. **Use Docker Compose with restart policy:**
   ```yaml
   restart: unless-stopped
   ```

2. **Set resource limits** (see docker-compose.yml)

3. **Enable log rotation** (already configured)

4. **Set up monitoring:**
   ```bash
   # Add to cron
   */5 * * * * docker inspect telegram-store-bot | grep Running
   ```

5. **Backup automation:**
   ```bash
   # Daily backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   cp data/stores.db backups/stores-$DATE.db
   ```

### Running as a Service

Create systemd service (Linux):

```bash
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Store Follow Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/scamvenge-telegram-bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## Security

### Best Practices

1. **Protect .env file:**
   ```bash
   chmod 600 .env
   ```

2. **Run as non-root** (already configured in Dockerfile)

3. **Limit network access** (if needed):
   ```yaml
   # In docker-compose.yml
   networks:
     telegram-network:
       driver: bridge
   ```

4. **Regular updates:**
   ```bash
   docker pull python:3.10-slim
   ./docker-helper.sh build
   ```

## Cleanup

### Remove Everything
```bash
# Using helper (interactive)
./docker-helper.sh clean

# Manual
docker-compose down -v --rmi local
```

### Remove Unused Docker Resources
```bash
docker system prune -a
```

## Troubleshooting

### "docker-compose: command not found"

**Problem:** You have Docker Compose v2 but the command is `docker compose` (space) not `docker-compose` (hyphen).

**Solution:** The `docker-helper.sh` script automatically detects and uses the correct command. Just use:
```bash
./docker-helper.sh build
```

If you're running commands manually, use:
```bash
# Docker Compose v2 (built into Docker)
docker compose up -d

# Docker Compose v1 (standalone)
docker-compose up -d
```

### Container Won't Start
```bash
# Check logs
docker-compose logs

# Check configuration
docker-compose config

# Rebuild
docker-compose build --no-cache
```

### Database Permission Issues

**Problem:** `unable to open database file` error on Linux VPS.

**Cause:** Container runs as UID 1000 by default, but your VPS user is different (often root = UID 0).

**Solution 1 - Run as Root (Recommended for VPS):**
```bash
# Add to your .env file:
echo "PUID=0" >> .env
echo "PGID=0" >> .env

# Restart
./docker-helper.sh stop
./docker-helper.sh start
```

**Solution 2 - Fix Directory Permissions:**
```bash
# Create directories with proper ownership
mkdir -p data .sessions logs temp
chown -R 1000:1000 data/ .sessions/ logs/ temp/
chmod -R 755 data/ .sessions/ logs/ temp/
```

**Solution 3 - Match Host User:**
```bash
# Set PUID/PGID to your current user
echo "PUID=$(id -u)" >> .env
echo "PGID=$(id -g)" >> .env
./docker-helper.sh restart
```

### Out of Disk Space
```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a
```

### Network Issues
```bash
# Check network
docker network ls
docker network inspect scamvenge-telegram-bot_default
```

## Advanced Configuration

### Custom Dockerfile
```bash
# Build with custom Dockerfile
docker-compose build --build-arg PYTHON_VERSION=3.11
```

### GPU Support (Advanced)
```yaml
# In docker-compose.yml
services:
  telegram-bot:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

### Multiple Instances
```bash
# Copy directory
cp -r scamvenge-telegram-bot bot-instance-2
cd bot-instance-2

# Edit .env with different config
# Edit docker-compose.yml to change container name

# Start
docker-compose up -d
```

## Performance Tuning

### CPU Optimization
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'  # Increase for faster OCR
```

### Memory Optimization
```yaml
environment:
  - MALLOC_TRIM_THRESHOLD_=100000
  - MALLOC_MMAP_THRESHOLD_=100000
```

## Support

For issues with Docker setup:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test connectivity: `docker-compose exec telegram-bot ping google.com`
4. Check resources: `docker stats`

## Summary

**Quick commands:**
- Start: `./docker-helper.sh start`
- Logs: `./docker-helper.sh logs`
- Test: `./docker-helper.sh test`
- Stop: `./docker-helper.sh stop`

**Data persistence:** All important data is in `./data` and session files.

**Backup:** Copy `./data/` directory and `*.session` files.

**Update:** `git pull`, rebuild, restart.

#!/bin/bash
# Docker helper script for common operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if .env exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_msg "Creating .env from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env with your Telegram credentials before running the bot"
        exit 1
    fi
}

# Build the Docker image
build() {
    print_msg "Building Docker image..."
    docker-compose build
    print_msg "Build complete!"
}

# Start the bot in detached mode
start() {
    check_env
    print_msg "Starting bot in detached mode..."
    docker-compose up -d
    print_msg "Bot started! Use './docker-helper.sh logs' to view logs"
}

# Start the bot in foreground (with logs)
run() {
    check_env
    print_msg "Starting bot in foreground..."
    docker-compose up
}

# Stop the bot
stop() {
    print_msg "Stopping bot..."
    docker-compose down
    print_msg "Bot stopped!"
}

# Restart the bot
restart() {
    print_msg "Restarting bot..."
    docker-compose restart
    print_msg "Bot restarted!"
}

# View logs
logs() {
    docker-compose logs -f --tail=100
}

# Authenticate with Telegram (interactive)
auth() {
    check_env
    print_msg "🔐 Starting Telegram authentication..."
    print_warning "You will be prompted for a code sent to your Telegram account"
    docker-compose run --rm telegram-bot python authenticate.py
}

# Run in test mode
test() {
    check_env
    print_warning "Starting bot in TEST MODE (no forwarding, no database writes)"
    docker-compose run --rm -e TEST_MODE=true telegram-bot
}

# Run tests
run_tests() {
    print_msg "Running tests in Docker..."
    docker-compose run --rm telegram-bot pytest -v
}

# Shell into container
shell() {
    print_msg "Opening shell in container..."
    docker-compose exec telegram-bot /bin/bash
}

# Clean up (remove containers, volumes, images)
clean() {
    print_warning "This will remove containers, volumes, and images. Continue? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_msg "Cleaning up..."
        docker-compose down -v --rmi local
        print_msg "Cleanup complete!"
    else
        print_msg "Cleanup cancelled"
    fi
}

# Show status
status() {
    print_msg "Container status:"
    docker-compose ps
    echo ""
    print_msg "Resource usage:"
    docker stats --no-stream telegram-store-bot 2>/dev/null || echo "Container not running"
}

# Show help
help() {
    cat << EOF
Docker Helper Script for Telegram Store Follow Bot

Usage: ./docker-helper.sh [command]

Commands:
  build       Build the Docker image
  auth        Authenticate with Telegram (first-time setup)
  start       Start bot in detached mode (background)
  run         Start bot in foreground (with logs)
  stop        Stop the bot
  restart     Restart the bot
  logs        View bot logs (live)
  test        Run bot in TEST MODE (dry run)
  run-tests   Run the test suite
  shell       Open a shell in the container
  status      Show container status and resource usage
  clean       Remove containers, volumes, and images
  help        Show this help message

Examples:
  ./docker-helper.sh build         # Build image
  ./docker-helper.sh auth          # Authenticate (first time)
  ./docker-helper.sh start         # Start in background
  ./docker-helper.sh logs          # View logs
  ./docker-helper.sh test          # Test mode (no forwarding)
  ./docker-helper.sh stop          # Stop bot

EOF
}

# Main script logic
case "${1:-help}" in
    build)
        build
        ;;
    auth)
        auth
        ;;
    start)
        start
        ;;
    run)
        run
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    test)
        test
        ;;
    run-tests)
        run_tests
        ;;
    shell)
        shell
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac

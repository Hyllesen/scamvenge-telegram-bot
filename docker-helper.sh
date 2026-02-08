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

# Detect Docker Compose command (v2 vs v1)
detect_compose_cmd() {
    if docker compose version &>/dev/null; then
        echo "docker compose"
    elif docker-compose version &>/dev/null; then
        echo "docker-compose"
    else
        print_error "Docker Compose not found!"
        print_error "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Get Docker Compose command
DOCKER_COMPOSE=$(detect_compose_cmd)

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
    $DOCKER_COMPOSE build
    print_msg "Build complete!"
}

# Start the bot in detached mode
start() {
    check_env
    print_msg "Starting bot in detached mode..."
    $DOCKER_COMPOSE up -d
    print_msg "Bot started! Use './docker-helper.sh logs' to view logs"
}

# Start the bot in foreground (with logs)
run() {
    check_env
    print_msg "Starting bot in foreground..."
    $DOCKER_COMPOSE up
}

# Stop the bot
stop() {
    print_msg "Stopping bot..."
    $DOCKER_COMPOSE down
    print_msg "Bot stopped!"
}

# Restart the bot
restart() {
    print_msg "Restarting bot..."
    $DOCKER_COMPOSE restart
    print_msg "Bot restarted!"
}

# View logs
logs() {
    $DOCKER_COMPOSE logs -f --tail=100
}

# Authenticate with Telegram (interactive)
auth() {
    check_env
    print_msg "🔐 Starting Telegram authentication..."
    print_warning "You will be prompted for a code sent to your Telegram account"
    $DOCKER_COMPOSE run --rm telegram-bot python authenticate.py
}

# Run in test mode
test() {
    check_env
    print_warning "Starting bot in TEST MODE (no forwarding, no database writes)"
    $DOCKER_COMPOSE run --rm -e TEST_MODE=true telegram-bot
}

# Run tests
run_tests() {
    print_msg "Running tests in Docker..."
    $DOCKER_COMPOSE run --rm telegram-bot pytest -v
}

# Shell into container
shell() {
    print_msg "Opening shell in container..."
    $DOCKER_COMPOSE exec telegram-bot /bin/bash
}

# Clean up (remove containers, volumes, images)
clean() {
    print_warning "This will remove containers, volumes, and images. Continue? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_msg "Cleaning up..."
        $DOCKER_COMPOSE down -v --rmi local
        print_msg "Cleanup complete!"
    else
        print_msg "Cleanup cancelled"
    fi
}

# Show status
status() {
    print_msg "Container status:"
    $DOCKER_COMPOSE ps
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

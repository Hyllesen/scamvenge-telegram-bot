#!/bin/bash
# Fix permissions for Docker volumes

echo "Fixing permissions for Docker volumes..."

# Get current user ID and group ID
USER_ID=$(id -u)
GROUP_ID=$(id -g)

echo "Your User ID: $USER_ID"
echo "Your Group ID: $GROUP_ID"

# Update .env file if it exists
if [ -f .env ]; then
    # Check if PUID/PGID exist in .env
    if grep -q "^PUID=" .env; then
        sed -i.bak "s/^PUID=.*/PUID=$USER_ID/" .env
        echo "✓ Updated PUID in .env"
    else
        echo "PUID=$USER_ID" >> .env
        echo "✓ Added PUID to .env"
    fi
    
    if grep -q "^PGID=" .env; then
        sed -i.bak "s/^PGID=.*/PGID=$GROUP_ID/" .env
        echo "✓ Updated PGID in .env"
    else
        echo "PGID=$GROUP_ID" >> .env
        echo "✓ Added PGID to .env"
    fi
    
    rm -f .env.bak
else
    echo "⚠ .env file not found. Please copy from .env.example first:"
    echo "  cp .env.example .env"
    exit 1
fi

# Ensure directories exist and are writable
mkdir -p data data/images .sessions logs
chmod 755 data data/images .sessions logs

echo ""
echo "✅ Permissions fixed!"
echo ""
echo "Now restart the Docker container:"
echo "  ./docker-helper.sh stop"
echo "  ./docker-helper.sh start"

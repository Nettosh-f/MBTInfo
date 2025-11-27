#!/bin/bash
set -e

echo "🚀 MBTI Service - VPS Deployer"
echo "--------------------------------"

# Check if rsync is installed
if ! command -v rsync &> /dev/null; then
    echo "❌ Error: rsync is not installed. Please install it first."
    exit 1
fi

# Get Connection Details
read -p "Enter VPS IP Address: " VPS_IP
if [ -z "$VPS_IP" ]; then
    echo "❌ IP Address is required."
    exit 1
fi

read -p "Enter VPS User (default: root): " VPS_USER
VPS_USER=${VPS_USER:-root}

TARGET_DIR="~/mbti-app"

echo "--------------------------------"
echo "📡 Syncing files to $VPS_USER@$VPS_IP:$TARGET_DIR..."

# Create directory first
ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "mkdir -p $TARGET_DIR"

# Sync files (excluding heavy/unnecessary items)
rsync -avz --progress \
    --exclude 'venv' \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'node_modules' \
    --exclude 'input/*' \
    --exclude 'output/*' \
    --exclude '.env' \
    . "$VPS_USER@$VPS_IP:$TARGET_DIR"

# Sync .env separately (ask user if they want to copy local .env)
if [ -f .env ]; then
    read -p "❓ Do you want to upload your local .env file? (y/n): " UPLOAD_ENV
    if [[ "$UPLOAD_ENV" =~ ^[Yy]$ ]]; then
        scp .env "$VPS_USER@$VPS_IP:$TARGET_DIR/.env"
        echo "✅ .env uploaded"
    else
        echo "⚠️  Skipping .env upload. Make sure to create it on the server!"
    fi
fi

echo "--------------------------------"
echo "🔧 Running setup on server..."
ssh "$VPS_USER@$VPS_IP" "cd $TARGET_DIR && bash setup_remote.sh"

echo "--------------------------------"
echo "✅ Deployment finished!"

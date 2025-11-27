#!/bin/bash
set -e

echo "🚀 Starting Server Setup..."

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# 2. Create necessary directories for persistence
echo "📂 Creating data directories..."
mkdir -p output input
chmod 777 output input  # Ensure container can write

# 3. Configure Frontend
echo "⚙️ Configuring Frontend..."
export API_URL="/api"
export CONFIG_OUTPUT_PATH="./frontend/config.js"
chmod +x frontend/generate_config.sh
./frontend/generate_config.sh
echo "✅ Frontend configured with API_URL=$API_URL"

# 4. Deploy
echo "🐳 Building and starting containers..."
docker compose -f docker-compose.prod.yml down --remove-orphans
docker compose -f docker-compose.prod.yml up -d --build

echo "✨ Deployment Complete! Application should be live on http://$(curl -s ifconfig.me)"

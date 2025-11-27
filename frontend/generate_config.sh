#!/bin/sh

# Default to /api if API_URL is not set
API_URL=${API_URL:-"/api"}
# Default output path
OUTPUT_PATH=${CONFIG_OUTPUT_PATH:-"/usr/share/nginx/html/config.js"}

# Generate config.js
cat <<EOF > "$OUTPUT_PATH"
window.ENV = {
  API_URL: '${API_URL}'
};
EOF

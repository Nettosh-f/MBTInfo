// Configuration for MBTI Processing Service
// This file can be modified during deployment with actual API URL
window.ENV = {
  // When running with docker-compose (nginx frontend container):
  // API_URL is /api (nginx proxies to backend)
  // When running standalone or in production:
  // API_URL should be the full backend URL
  API_URL: '/api'  // For docker-compose setup - nginx will proxy to backend
};


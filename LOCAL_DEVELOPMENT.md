# Local Development Guide

## Running the Application Locally

### Prerequisites
- Docker installed

### Quick Start

#### 1. Start the Backend & Frontend

```bash
make up
```

#### 3. Access the Application

- **Frontend**: http://localhost
- **Backend**: http://localhost/api
- **Swaggers**: http://localhost/api/docs

### Configuration

#### Backend Configuration

Backend configuration is set via environment variables in an `.env` file.
Copy `.env.example` and add `OPENAI_API_KEY`.

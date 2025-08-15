# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- `python3 main.py` - Start the FastAPI server on localhost:8080
- `python3 -m uvicorn app.app:app --reload --host 0.0.0.0 --port 8000` - Alternative development server (port 8000)
- Access web interface at `http://0.0.0.0:8080/` (or port 8000 if using uvicorn directly)
- Access API docs at `http://0.0.0.0:8080/docs` (or port 8000 if using uvicorn directly)

### Testing
- `pytest ./ --cov=app --cov-report=term-missing` - Run tests with coverage report
- `scripts/tests.sh` - Alternative test script
- Tests are located in `app/usecase/tests/`

### Dependencies and Setup
- `pip install -r requirements.txt` - Install all dependencies
- Python 3.10 (as specified in Dockerfile)
- Virtual environment recommended

### Environment Setup
1. Rename `.env.example` to `.env` and update values (especially PROJECT_ROOT)
2. For local development, set `LOCAL_ENV=True` in .env
3. For GCP deployment, configure GCP_PROJECT_ID, GCP_SECRET_NAME, GCP_SECRET_VERSION

### Docker
- `docker build -t wine-tournament .` - Build Docker image
- Uses `tiangolo/uvicorn-gunicorn-fastapi:python3.10` base image
- Exposes port 8080

## Architecture Overview

This is a FastAPI application following Clean Architecture principles with dependency injection using the `inject` library.

### Layer Structure
- **API Layer** (`app/api/`) - FastAPI routers and endpoints
- **Use Cases** (`app/usecase/`) - Business logic implementation
- **Model/Domain** (`app/model/`) - Domain entities and repository interfaces
- **Repository** (`app/repository/`) - Data persistence implementations
- **Gateway** (`app/gateway/`) - External service integrations

### Key Components
- **Dependency Injection**: Configured in `app/config.py` using the `inject` library - binds interfaces to implementations
- **Configuration Management**: `python-decouple` for environment variables, supports both local .env and GCP Secret Manager
- **Wine Tournament**: Main application for managing wine tournaments with participant registration, voting, and leaderboards
- **Word Transformer**: Legacy example business logic (can be removed)
- **Repository Pattern**: Abstract repositories with JSON file implementations for data persistence
- **CORS**: Pre-configured for cross-origin requests with wildcard origins
- **Static File Serving**: Single-page application served from `/static` directory
- **Logging**: Uses `loguru` with GCP Cloud Logging support

## Wine Tournament Features

### Core Functionality
1. **Participant Management**: Add participants with random wine assignments (5 wines per participant, max 5 participants per wine)
2. **Wine Assignment**: Casino-style slot machine UI for wine selection with constraint validation
3. **Voting System**: Participants rank their top 3 wines (3, 2, 1 points)
4. **Leaderboard**: Real-time scoring and ranking display
5. **Elegant UI**: Apple-inspired design with vineyard background, golden casino slots, and burgundy/violet theme

### API Endpoints
- `POST /api/v1/tournament/participants/suggest` - Generate wine suggestions for new participant
- `POST /api/v1/tournament/participants/confirm` - Confirm and save participant
- `GET /api/v1/tournament/participants` - List all participants
- `POST /api/v1/tournament/votes` - Submit vote rankings
- `GET /api/v1/tournament/leaderboard` - Get current leaderboard

### Data Storage
- Participants stored in `data/participants.json`
- Votes stored in `data/votes.json`
- Automatic directory and file creation
- JSON-based repository implementation with in-memory caching

### Configuration
- Uses `python-decouple` for environment variable management
- Supports GCP Secret Manager for production environments
- Local development uses `.env` file when `LOCAL_ENV=True`

### Frontend
- Single-page application in `static/index.html`
- Apple-inspired CSS design with wine theme in `static/css/style.css`
- Casino slot machine animations and real-time updates in `static/js/app.js`
- Vineyard background image with blur effects
- Golden-bordered casino slots with burgundy/violet color scheme

### Testing
- Uses pytest with async support (`pytest-asyncio`)
- Code coverage reporting with `pytest-cov`
- Test configuration in `pyproject.toml` sets pythonpath
- Main tests in `app/usecase/tests/`

### Important Implementation Notes
- Wine assignment algorithm handles edge cases when tournament is nearly full
- Casino slot machine UI provides visual feedback for wine selection
- Real-time capacity tracking prevents wine over-assignment
- Constraint validation ensures no wine has more than 5 participants
- Responsive design works on mobile and desktop
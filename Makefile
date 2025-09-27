# Game Overlay AI - Development Makefile

.PHONY: help install dev test lint format clean docker-build docker-run docker-dev setup setup-linux setup-docker dev-backend dev-frontend dev-full db-init db-migrate etl-sample etl-minecraft health check-deps install-uv electron-install electron-dev start-background stop-background

# Default target
help:
	@echo "Game Overlay AI - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup           Full setup (install + db-init + etl-sample)"
	@echo "  setup-linux     Linux-specific setup with instructions"
	@echo "  setup-docker    Docker setup"
	@echo ""
	@echo "Development:"
	@echo "  install         Install dependencies with uv"
	@echo "  dev             Run development server"
	@echo "  dev-backend     Run backend only"
	@echo "  dev-frontend    Run frontend only"
	@echo "  dev-full        Show instructions for full development"
	@echo "  test            Run tests with pytest"
	@echo "  lint            Run linting checks"
	@echo "  format          Format code with black and isort"
	@echo "  clean           Clean up temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run production container"
	@echo "  docker-dev      Run development container"
	@echo "  docker-stop     Stop all containers"
	@echo ""
	@echo "Database:"
	@echo "  db-init         Initialize database"
	@echo "  db-migrate      Run database migrations"
	@echo ""
	@echo "ETL:"
	@echo "  etl-sample      Run sample ETL pipeline"
	@echo "  etl-minecraft   Ingest Minecraft data"
	@echo ""
	@echo "Utilities:"
	@echo "  health          Check if backend is running"
	@echo "  check-deps      Check system dependencies"
	@echo "  install-uv      Install uv package manager"
	@echo "  electron-install Install Electron dependencies"
	@echo "  electron-dev     Run Electron in development mode"
	@echo ""
	@echo "Linux Background Services:"
	@echo "  start-background Start services in tmux sessions"
	@echo "  stop-background  Stop background services"

# Development commands
install:
	@echo "Installing Python dependencies..."
	uv pip install -e ".[dev]" || (echo "Editable install failed, trying system install..." && \
		uv pip install --system fastapi uvicorn sqlalchemy pydantic pydantic-settings chromadb sentence-transformers google-generativeai requests beautifulsoup4 python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv httpx aiofiles && \
		uv pip install --system pytest pytest-asyncio pytest-cov black isort flake8 mypy pre-commit)
	@echo "Installing Electron dependencies..."
	cd static && npm install
	@echo "Dependencies installed successfully"

dev:
	@echo "Starting development server..."
	@echo "Backend will be available at: http://localhost:8000"
	@echo "API documentation: http://localhost:8000/docs"
	@echo "Press Ctrl+C to stop"
	uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

test-watch:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing -f

lint:
	uv run flake8 src/ tests/
	uv run mypy src/
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/

format:
	uv run black src/ tests/
	uv run isort src/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

# Docker commands
docker-build:
	docker build -t game-overlay-ai:latest .

docker-run:
	docker-compose up -d backend

docker-dev:
	docker-compose --profile dev up -d backend-dev

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

# Database commands
db-init:
	@echo "Initializing database..."
	uv run python -c "from src.db.database import create_tables; create_tables(); print('Database initialized')" || \
		(echo "uv run failed, trying direct python..." && \
		python -c "from src.db.database import create_tables; create_tables(); print('Database initialized')")

db-migrate:
	@echo "Running database migrations..."
	uv run alembic upgrade head || \
		(echo "uv run failed, trying direct python..." && \
		python -m alembic upgrade head)

# ETL commands
etl-sample:
	@echo "Running sample ETL pipeline..."
	uv run python scripts/etl_sample_data.py || \
		(echo "uv run failed, trying direct python..." && \
		python scripts/etl_sample_data.py)

etl-minecraft:
	@echo "Running Minecraft ETL pipeline..."
	uv run python scripts/etl_minecraft_data.py || \
		(echo "uv run failed, trying direct python..." && \
		python scripts/etl_minecraft_data.py)

# Setup commands
setup: install db-init etl-sample
	@echo "Setup complete! Run 'make dev' to start development server"

setup-linux: install db-init etl-sample
	@echo "Linux setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env file and add your API keys"
	@echo "  2. Start backend: make dev"
	@echo "  3. Start frontend: make electron-dev"
	@echo "  4. Or run both: make dev-full"

setup-docker: docker-build
	@echo "Docker setup complete! Run 'make docker-run' to start production"

# Electron frontend commands
electron-install:
	cd static && npm install

electron-dev:
	cd static && npm run dev

electron-build:
	cd static && npm run build

# Full development setup
setup-full: install electron-install db-init
	@echo "Full setup complete!"
	@echo "Backend: make dev"
	@echo "Frontend: make electron-dev"

# Production deployment
deploy:
	docker-compose up -d
	@echo "Production deployment complete!"

# Health checks
health:
	@echo "Checking backend health..."
	curl -f http://localhost:8000/api/v1/health || echo "Backend not responding"

# Linux-specific utilities
check-deps:
	@echo "Checking system dependencies..."
	@command -v python3 >/dev/null 2>&1 || echo "❌ Python3 not found"
	@command -v node >/dev/null 2>&1 || echo "❌ Node.js not found"
	@command -v npm >/dev/null 2>&1 || echo "❌ npm not found"
	@command -v uv >/dev/null 2>&1 || echo "❌ uv not found"
	@echo "✅ Dependency check complete"

install-uv:
	@echo "Installing uv package manager..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "Please restart your shell or run: source ~/.bashrc"

# Process management for Linux
start-background:
	@echo "Starting services in background..."
	@echo "Backend: tmux session 'backend'"
	@echo "Frontend: tmux session 'frontend'"
	tmux new-session -d -s backend 'make dev-backend'
	tmux new-session -d -s frontend 'make dev-frontend'
	@echo "Services started! Use 'tmux attach -t backend' to view backend logs"
	@echo "Use 'tmux attach -t frontend' to view frontend logs"

stop-background:
	@echo "Stopping background services..."
	tmux kill-session -t backend 2>/dev/null || true
	tmux kill-session -t frontend 2>/dev/null || true
	@echo "Services stopped"

# Development workflow
dev-backend:
	@echo "Starting backend server..."
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Press Ctrl+C to stop"
	uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload || \
		(echo "uv run failed, trying direct python..." && \
		python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload)

dev-frontend:
	@echo "Starting Electron frontend..."
	@echo "Frontend: Electron overlay window"
	@echo "Press Ctrl+C to stop"
	cd static && npm run dev

dev-full:
	@echo "Starting full development environment..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: Electron overlay"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Run in separate terminals:"
	@echo "  Terminal 1: make dev-backend"
	@echo "  Terminal 2: make dev-frontend"
	@echo ""
	@echo "Or use tmux/screen for background processes:"
	@echo "  tmux new-session -d -s backend 'make dev-backend'"
	@echo "  tmux new-session -d -s frontend 'make dev-frontend'"

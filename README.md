# Game Overlay AI

An AI-powered game overlay that provides contextual walkthroughs and tips while you play, similar to Cluely. Built with FastAPI backend and Electron frontend.

## 🎮 Features

- **Real-time Game Tips**: Get contextual help while playing any game
- **AI-Powered RAG Pipeline**: Uses vector databases and LLMs for intelligent tip generation
- **Transparent Overlay**: Always-on-top transparent window that doesn't interfere with gameplay
- **Multi-Game Support**: Works with Minecraft, Elden Ring, Cyberpunk 2077, and more
- **Smart ETL Pipeline**: Automatically ingests game guides, wikis, and forums
- **RESTful API**: Clean API for tip retrieval and management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Electron      │    │   FastAPI       │    │   Vector DB     │
│   Overlay       │◄──►│   Backend       │◄──►│   (ChromaDB)    │
│   (Frontend)    │    │   (Python)      │    │                │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │   (Gemini)      │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- uv (Python package manager)
- Git

### Installation

#### 🪟 Windows (Easy Setup)

1. **Clone the repository**
   ```cmd
   git clone https://github.com/gameoverlayai/game-overlay-ai.git
   cd game-overlay-ai
   ```

2. **Run the Windows setup script**
   ```cmd
   setup-windows.bat
   ```
   This will automatically:
   - Install uv and Python dependencies
   - Install Electron dependencies
   - Create .env file from template
   - Initialize the database
   - Run sample ETL pipeline

3. **Edit your API keys**
   - Open `.env` file
   - Add your `GEMINI_API_KEY` and optionally `OPENAI_API_KEY`

4. **Start development**
   ```cmd
   start-dev.bat
   ```
   Or start services separately:
   ```cmd
   start-backend.bat    # Terminal 1
   start-overlay.bat    # Terminal 2
   ```

#### 🐧 Linux/macOS (Easy Setup)

1. **Clone the repository**
   ```bash
   git clone https://github.com/gameoverlayai/game-overlay-ai.git
   cd game-overlay-ai
   ```

2. **Check dependencies**
   ```bash
   make check-deps
   ```

3. **Install uv if needed**
   ```bash
   make install-uv
   # Restart your shell or run: source ~/.bashrc
   ```

4. **Run Linux setup**
   ```bash
   make setup-linux
   ```
   This will automatically:
   - Install Python dependencies with fallback options
   - Install Electron dependencies
   - Create .env file from template
   - Initialize the database
   - Run sample ETL pipeline

5. **Edit your API keys**
   - Open `.env` file
   - Add your `GEMINI_API_KEY` and optionally `OPENAI_API_KEY`

6. **Start development**
   ```bash
   # Option 1: Manual (recommended for development)
   make dev-backend    # Terminal 1
   make dev-frontend   # Terminal 2
   
   # Option 2: Background services (Linux)
   make start-background
   # View logs: tmux attach -t backend
   # Stop: make stop-background
   ```

### Development

#### 🪟 Windows Development

**Option 1: Use batch files (Recommended)**
```cmd
# Start both backend and overlay
start-dev.bat

# Or start separately
start-backend.bat    # Terminal 1
start-overlay.bat    # Terminal 2
```

**Option 2: Manual commands**
```cmd
# Start backend
uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# Start overlay (in another terminal)
cd static
npm run dev
```

#### 🐧 Linux/macOS Development

**Option 1: Manual Development (Recommended)**
```bash
# Terminal 1: Start backend
make dev-backend

# Terminal 2: Start frontend
make dev-frontend
```

**Option 2: Background Services (Linux)**
```bash
# Start both services in background
make start-background

# View backend logs
tmux attach -t backend

# View frontend logs
tmux attach -t frontend

# Stop services
make stop-background
```

**Option 3: Individual Commands**
```bash
# Backend only
make dev

# Frontend only
make electron-dev

# Check if backend is running
make health
```

#### 📚 Access the API documentation
- Open http://localhost:8000/docs for Swagger UI
- Open http://localhost:8000/redoc for ReDoc

## 📖 API Usage

### Get Tips for a Game

```bash
# Basic tips for Minecraft
curl "http://localhost:8000/api/v1/tips?game=minecraft"

# Search for specific tips
curl "http://localhost:8000/api/v1/tips?game=minecraft&query=redstone"

# Filter by category and difficulty
curl "http://localhost:8000/api/v1/tips?game=minecraft&category=beginner&difficulty=easy"
```

### Create a New Tip

```bash
curl -X POST "http://localhost:8000/api/v1/tips" \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": 1,
    "title": "Advanced Redstone Contraptions",
    "content": "Create complex redstone machines using comparators and repeaters...",
    "category": "advanced",
    "difficulty": "hard"
  }'
```

## 🧪 Testing

#### 🪟 Windows Testing

```cmd
# Run all tests
test-windows.bat

# Or manually
uv run pytest tests/ -v --cov=src --cov-report=html
```

#### 🐧 Linux/macOS Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test

# Run tests in watch mode
make test-watch

# Run specific test file
uv run pytest tests/test_tips_api.py -v

# Check system dependencies
make check-deps
```

## 🐳 Docker Deployment

### Development

```bash
# Build and run development container
make docker-dev

# View logs
make docker-logs
```

### Production

```bash
# Build production image
make docker-build

# Run production container
make docker-run

# Stop containers
make docker-stop
```

## 📁 Project Structure

```
game-overlay-ai/
├── src/                    # Backend source code
│   ├── db/                # Database models and connections
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── repositories/      # Data access layer
│   ├── services/          # Business logic
│   │   ├── rag_service.py     # RAG pipeline
│   │   ├── etl_service.py     # ETL operations
│   │   ├── agent_service.py   # AI agent logic
│   │   └── overlay_service.py # Overlay management
│   ├── routers/           # FastAPI routers
│   ├── middlewares/       # Custom middleware
│   ├── exceptions/        # Custom exceptions
│   └── main.py           # Application entry point
├── static/               # Electron frontend
│   ├── index.html        # Overlay UI
│   ├── main.js          # Electron main process
│   ├── preload.js       # Preload script
│   └── package.json     # Node.js dependencies
├── tests/               # Test suite
├── scripts/             # ETL and utility scripts
├── notebooks/           # Jupyter notebooks for experiments
├── pyproject.toml       # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── Makefile           # Development commands
└── README.md          # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `127.0.0.1` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `true` |
| `DATABASE_URL` | Database connection | `sqlite:///./game_overlay.db` |
| `GEMINI_API_KEY` | Gemini API key | Required for LLM features |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB directory | `./chroma_db` |

### API Keys Setup

1. **Gemini API Key** (for LLM features):
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `.env`: `GEMINI_API_KEY=your_key_here`

2. **OpenAI API Key** (optional alternative):
   - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Add to `.env`: `OPENAI_API_KEY=your_key_here`

## 🎯 Usage Examples

### Basic Game Tips

```python
import requests

# Get tips for Minecraft
response = requests.get("http://localhost:8000/api/v1/tips?game=minecraft")
tips = response.json()

for tip in tips["tips"]:
    print(f"Title: {tip['title']}")
    print(f"Content: {tip['content']}")
    print(f"Category: {tip['category']}")
    print("---")
```

### ETL Pipeline

```python
from src.services.etl_service import ETLService

# Initialize ETL service
etl = ETLService()

# Extract from URL
documents = etl.extract_from_url("https://minecraft.fandom.com/wiki/Tutorials")

# Load into vector database
success = etl.load_to_vector_db(documents)
```

### RAG Pipeline

```python
from src.services.rag_service import RAGService

# Initialize RAG service
rag = RAGService()

# Get contextual tips
tips = rag.get_tips_with_rag(
    query="How do I build a house?",
    game="minecraft",
    limit=5
)
```

## 🛠️ Development

### Linux-Specific Features

The Makefile includes several Linux-specific utilities for better development experience:

```bash
# Check system dependencies
make check-deps

# Install uv package manager
make install-uv

# Start services in background with tmux
make start-background

# Stop background services
make stop-background

# View help for all available commands
make help
```

### Code Quality

#### 🪟 Windows

```cmd
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Run linting
uv run flake8 src/ tests/
uv run mypy src/
```

#### 🐧 Linux/macOS

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make lint

# Clean up temporary files
make clean

# Check system dependencies
make check-deps
```

### Database Migrations

#### 🪟 Windows

```cmd
# Create migration
uv run alembic revision --autogenerate -m "Add new table"

# Apply migrations
uv run alembic upgrade head
```

#### 🐧 Linux/macOS

```bash
# Create migration
uv run alembic revision --autogenerate -m "Add new table"

# Apply migrations
make db-migrate

# Initialize database
make db-init
```

### Adding New Games

1. **Create game data**:
   ```python
   from src.repositories.tip_repository import TipRepository
   
   # Add game
   game = tip_repo.get_or_create_game("new_game")
   ```

2. **Run ETL pipeline**:
   ```bash
   # Linux/macOS
   make etl-sample
   
   # Windows
   uv run python scripts/etl_sample_data.py
   ```

3. **Test retrieval**:
   ```bash
   # Linux/macOS
   curl "http://localhost:8000/api/v1/tips?game=new_game"
   
   # Windows (PowerShell)
   Invoke-RestMethod "http://localhost:8000/api/v1/tips?game=new_game"
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `make test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints for better code clarity
- Write clear commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [ChromaDB](https://www.trychroma.com/) for vector database capabilities
- [Electron](https://www.electronjs.org/) for cross-platform desktop apps
- [Google Gemini](https://ai.google.dev/) for LLM capabilities

## 📞 Support

- 📧 Email: support@gameoverlayai.com
- 🐛 Issues: [GitHub Issues](https://github.com/gameoverlayai/game-overlay-ai/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/gameoverlayai/game-overlay-ai/discussions)

---

**Happy Gaming! 🎮✨**

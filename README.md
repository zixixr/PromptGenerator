# Prompt Optimizer

Automated prompt iteration system for optimizing LLM prompts against custom evaluation criteria.

## Features

- **Multi-turn Conversation Simulation**: Test prompts with realistic user interactions
- **Custom Evaluation Criteria**: Define specific quality metrics for your use case
- **Automated Rewriting**: LLM-powered prompt refinement based on evaluation feedback
- **Iteration Tracking**: Monitor optimization progress across multiple iterations
- **Multiple LLM Support**: OpenAI, Anthropic, Google, and custom endpoints
- **Secure Credential Storage**: Encrypted API key management
- **Export Results**: JSON and CSV export formats

## Architecture

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, LangChain
- **Frontend**: React 18, TypeScript, Vite, Zustand
- **Database**: SQLite (local storage)
- **Security**: Fernet symmetric encryption for credentials

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- pip and npm

### Backend Setup

```bash
cd backend
pip install -e .
python -m src.main
```

Backend will run on http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:5173

### Configuration

1. Navigate to Settings page in the UI
2. Add your LLM provider API keys (OpenAI, Anthropic, Google)
3. Keys are encrypted and stored in `data/credentials.enc`

## Usage

### Creating a Project

1. Click "New Project"
2. Enter project name and initial system prompt
3. Select target LLM model
4. Add test scenarios (conversation templates)
5. Define evaluation criteria with thresholds
6. Click "Create Project"

### Running Optimization

1. Open project details
2. Click "Start Optimization"
3. System will:
   - Simulate conversations for each test scenario
   - Evaluate against all criteria
   - Automatically rewrite prompt if criteria fail
   - Iterate until success or max iterations reached

### Exporting Results

- Click "Export JSON" for detailed results
- Click "Export CSV" for summary data
- Export includes:
  - Final optimized prompt
  - All iteration results
  - Evaluation scores and feedback

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── api/          # FastAPI routes
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── services/     # Business logic
│   │   ├── storage/      # Database and encryption
│   │   └── main.py       # Application entry point
│   └── tests/            # Contract and integration tests
│
├── frontend/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # API client
│   │   └── store/        # State management
│   └── index.html
│
├── config/               # Configuration files
├── specs/                # Feature specifications and design docs
└── README.md
```

## Development

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Development

```bash
cd frontend
npm run dev    # Development server
npm run build  # Production build
npm run lint   # Lint code
```

### Configuration

Edit `config/default.yaml` to adjust:
- Default iteration limits
- LLM timeouts
- Temperature settings

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security Notes

- API keys are encrypted using Fernet symmetric encryption
- Encryption key stored in `data/encryption.key` (0600 permissions)
- Credentials stored in `data/credentials.enc`
- Single-user local application (no authentication required)

## License

MIT License - see LICENSE file for details

# XTREMEDEV Copilot Instructions

## Project Overview
This is a **Docker Model Runner (DMR) analysis toolkit** for testing and documenting local AI model capabilities through OpenAI-compatible APIs. The project focuses on systematic model testing, capability discovery, and comprehensive documentation generation.

## Architecture & Key Components

### DMR Integration Pattern
- **Primary Connection**: `http://localhost:12434/engines/v1` (DMR with TCP enabled)
- **Container Connection**: `http://model-runner.docker.internal/engines/v1`
- **API Compatibility**: Full OpenAI-compatible endpoints (chat/completions, embeddings, models)
- **Authentication**: Uses dummy API keys (e.g., `sk-local-123`) as DMR doesn't validate them

### Core Analysis Framework (`DMR/get_model_info.py`)
The main analyzer follows a **comprehensive testing pattern**:

```python
class DMRModelAnalyzer:
    def __init__(self, base_url="http://localhost:12434/engines/v1"):
        # Session with persistent headers for efficiency
    
    def analyze_model(self, model_data) -> ModelInfo:
        # Tests applied conditionally based on model type
        # Embedding models: Skip chat tests, only test embeddings
        # Chat models: Test all capabilities (function calling, JSON, streaming, parameters)
```

**Test Categories** (each isolated with 30s timeouts):
1. **Function Calling**: Tool/function definition validation with weather API example
2. **JSON Mode**: Structured output with `response_format: {type: "json_object"}`
3. **Streaming**: SSE chunk counting and validation
4. **Parameters**: OpenAI parameter support (temperature, max_tokens, top_p, penalties, stop)
5. **Embeddings**: Vector generation with dimension reporting

### Data Models & Output
- **`ModelCapabilities`**: Structured capability flags and parameter lists
- **`ModelInfo`**: Complete model metadata with test results
- **JSON Output**: `dmr_model_analysis.json` with timestamped, comprehensive analysis data

## Development Workflow

### Setup & Dependencies
```bash
# Virtual environment (recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Minimal dependencies
pip install -r DMR/requirements.txt  # Only requests>=2.28.0
```

### Running Analysis
```bash
# From DMR directory
cd DMR
python get_model_info.py
```

**Expected Output**:
- Real-time console progress with emoji indicators (🔍 🚀 ✅ ❌)
- `dmr_model_analysis.json` with complete capability matrix
- Summary table showing capability support across all models

### Model Classification Patterns
- **Chat Models**: `ai/gemma3`, `ai/qwen3`, `hf.co/lmstudio-community/*` - Full capability testing
- **Embedding Models**: `ai/embed*`, `ai/mxbai*` - Embeddings-only testing
- **Auto-detection**: Model naming conventions determine test suite application

## Project-Specific Conventions

### Error Handling Philosophy
- **Graceful Degradation**: Each test is isolated; failures don't cascade
- **Detailed Logging**: Comprehensive error capture in JSON results
- **Timeout Management**: All HTTP calls have explicit 30s timeouts
- **Partial Success**: Individual parameter testing on bulk parameter failure

### Code Patterns
- **Dataclass Usage**: `@dataclass` with `asdict()` for JSON serialization
- **Session Reuse**: Single `requests.Session` for connection pooling
- **Type Hints**: Comprehensive typing with `Optional`, `List`, `Dict`
- **Structured Logging**: Emoji-prefixed console output for user feedback

### Testing Methodology
```python
# Conditional testing pattern
if not model_id.lower().startswith(('ai/embed', 'ai/mxbai')):
    # Chat model - test all capabilities
else:
    # Embedding model - skip chat tests
```

## DMR-Specific Knowledge

### Connection Requirements
- **DMR Must Be Running**: Docker Desktop with Model Runner enabled
- **TCP Mode**: Host-side TCP support enabled (typically port 12434)
- **Model Availability**: Models must be pulled via `docker model pull` before testing

### Model Endpoint Patterns
```python
# Standard endpoints used by analyzer
GET  /models                    # Model discovery
POST /chat/completions         # Chat & function calling
POST /embeddings              # Vector generation
```

### Known Model Behaviors
- **Qwen Models**: Support `reasoning_content` in streaming responses
- **Gemma Models**: Standard OpenAI-compatible responses
- **Embedding Models**: Different dimension outputs (768 vs 1024)
- **Function Calling**: Models vary in argument formatting and reasoning inclusion

## File Structure & Documentation
```
DMR/
├── get_model_info.py          # Main analysis engine
├── requirements.txt           # Minimal dependencies
├── dmr_model_analysis.json    # Generated results (ignored in .gitignore)
└── README.md                  # User documentation

docker-model-runner.md         # DMR API reference & cheat sheet
```

## Integration Guidelines

### When Extending Functionality
1. **Add New Tests**: Extend `DMRModelAnalyzer` with new test methods following the timeout pattern
2. **Update Capabilities**: Add new boolean flags to `ModelCapabilities` dataclass
3. **Maintain Isolation**: Ensure new tests don't affect existing test reliability
4. **Document Results**: Update README.md with new capability descriptions

### API Client Patterns
Follow the established OpenAI SDK pattern for consistency:
```python
client = OpenAI(
    api_key="sk-local-123",
    base_url="http://localhost:12434/engines/v1"
)
```

### Performance Considerations
- **Analysis Time**: ~30-60 seconds per model (function calling tests are slowest)
- **Parallel Execution**: Avoid - DMR performs better with sequential requests
- **Resource Usage**: Minimal - only HTTP requests, no model loading required
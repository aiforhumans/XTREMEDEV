# DMR Model Analysis Tool

This directory contains tools for analyzing Docker Model Runner (DMR) capabilities and storing comprehensive model information.

## Files

- **`get_model_info.py`** - Main analysis script that tests all model capabilities
- **`requirements.txt`** - Python dependencies
- **`dmr_model_analysis.json`** - Generated analysis results (created after running the script)

## Features

The analysis script automatically tests and documents:

### 🔧 Function Calling
- Tests OpenAI-compatible function/tool calling
- Verifies proper tool_calls response format
- Includes sample weather function definition

### 📄 JSON Mode  
- Tests structured JSON response formatting
- Validates `response_format: {type: "json_object"}` parameter
- Extracts structured data from text

### 🌊 Streaming
- Tests Server-Sent Events (SSE) streaming
- Validates real-time token delivery
- Counts streaming chunks

### 🔢 Embeddings
- Tests vector embedding generation
- Reports embedding dimensions
- Shows sample embedding values

### ⚙️ Parameter Support
- Tests OpenAI API parameters:
  - `temperature` - Controls randomness (0.0-2.0)
  - `max_tokens` - Response length limit
  - `top_p` - Nucleus sampling
  - `frequency_penalty` - Reduces repetition
  - `presence_penalty` - Encourages diversity
  - `stop` - Stop sequences

## Usage

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Run Analysis
```bash
python get_model_info.py
```

### Output
The script generates:
1. **Console output** - Real-time analysis progress and summary
2. **JSON file** - Detailed test results and capabilities data

## Analysis Results

### Chat Models (Support full conversational AI)
- ✅ `ai/gemma3:latest` - Full capabilities
- ✅ `ai/qwen3:latest` - Full capabilities  
- ✅ `ai/gemma3n:latest` - Full capabilities
- ✅ `hf.co/lmstudio-community/qwen3-4b-gguf:q4_k_m` - Full capabilities

### Embedding Models (Vector generation only)
- ✅ `ai/embeddinggemma:latest` - 768 dimensions
- ✅ `ai/mxbai-embed-large:latest` - 1024 dimensions

## DMR Connection

The script connects to Docker Model Runner at:
- **Default URL**: `http://localhost:12434/engines/v1`
- **Requirements**: DMR must be running with TCP enabled

## JSON Output Structure

```json
{
  "analysis_date": "2025-09-15T19:54:35.755792",
  "dmr_endpoint": "http://localhost:12434/engines/v1", 
  "total_models": 6,
  "models": [
    {
      "id": "ai/gemma3:latest",
      "capabilities": {
        "supports_function_calling": true,
        "supports_json_mode": true,
        "supports_streaming": true,
        "supports_embeddings": false,
        "supported_parameters": ["temperature", "max_tokens", ...]
      },
      "test_results": {
        "function_calling": { /* detailed test data */ },
        "json_mode": { /* detailed test data */ },
        "streaming": { /* detailed test data */ },
        "parameters": { /* detailed test data */ }
      }
    }
  ]
}
```

## Customization

### Change DMR Endpoint
```python
analyzer = DMRModelAnalyzer(base_url="http://your-dmr-host:port/engines/v1")
```

### Add Custom Tests
Extend the `DMRModelAnalyzer` class with additional test methods:

```python
def test_custom_feature(self, model_id: str) -> Dict[str, Any]:
    # Your custom test logic here
    pass
```

## Error Handling

The script gracefully handles:
- Connection failures to DMR
- Model-specific capability limitations  
- Timeout scenarios for long-running tests
- Invalid responses or API errors

Each test is isolated - failures in one test don't affect others.

## Performance Notes

- Analysis takes ~30-60 seconds per model
- Embedding tests are fastest
- Function calling tests take longest
- All tests have 30-second timeouts

## Automation

Run analysis on schedule to track model updates:
```bash
# Daily analysis
python get_model_info.py > analysis_$(date +%Y%m%d).log
```
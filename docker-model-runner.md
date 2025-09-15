# DMR ↔ OpenAI API Cheat Sheet

## 0) Enable Model Runner

**Docker Desktop** → Settings → AI → Enable Docker Model Runner, optionally:

- Enable GPU-backed inference (Windows + supported NVIDIA GPU)
- Enable host-side TCP support (choose a port, e.g. 12434)
- (If calling from a browser frontend) add your CORS Allowed Origins.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/)

**Docker Engine (Linux servers)**: install the plugin (docker-model-plugin). TCP is enabled by default on 12434.

[Docker Documentation](https://docs.docker.com/engine/model-runner/)

## 1) Base URLs you'll point clients at

- **From containers**: `http://model-runner.docker.internal/engines/v1`
- **From host processes (with TCP enabled)**: `http://localhost:12434/engines/v1`

**Compose tip (Linux Engine)**: add `extra_hosts: ["model-runner.docker.internal:host-gateway"]` if 172.17.0.1 isn't reachable.

[Docker Documentation](https://docs.docker.com/compose/networking/)

DMR exposes OpenAI-compatible endpoints (chat/completions, completions, embeddings, models) under `/engines/v1/...`. You may also see the fully qualified `.../engines/llama.cpp/v1/...`; the `/llama.cpp` segment is optional.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

## 2) Pull a model (one-time)

```bash
# From Docker Hub curated models
docker model pull ai/smollm2:360M-Q4_K_M

# Direct from Hugging Face
docker model pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF
```

Models are cached locally; DMR will load on demand when first requested.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/get-started/)

## 3) Minimal cURL calls

### Inside a container
```bash
curl http://model-runner.docker.internal/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/smollm2:360M-Q4_K_M",
    "messages": [{"role":"user","content":"Hello!"}]
  }'
```

### From the host over TCP
```bash
curl http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/smollm2:360M-Q4_K_M",
    "messages": [{"role":"user","content":"Hello!"}]
  }'
```

API paths and examples per docs.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

Unix socket variant also exists (prefix with `/exp/vDD4.40` before `/engines/...`) if you want to hit the Docker socket directly.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

## 4) OpenAI SDK snippets

**API key**: most clients require one; DMR doesn't validate it. Use any dummy value (e.g., `sk-local-123`). Point base URL to DMR.

### Python (openai>=1.x)
```python
from openai import OpenAI
client = OpenAI(
    api_key="sk-local-123",
    base_url="http://localhost:12434/engines/v1"  # or model-runner.docker.internal from containers
)

resp = client.chat.completions.create(
    model="ai/smollm2:360M-Q4_K_M",
    messages=[{"role":"user","content":"Summarize Docker Model Runner in 2 lines."}]
)
print(resp.choices[0].message.content)
```

DMR supports chat/completions, completions, embeddings, and models endpoints.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

### Node/TypeScript (official openai client)
```typescript
import OpenAI from "openai";
const openai = new OpenAI({
  apiKey: "sk-local-123",
  baseURL: "http://localhost:12434/engines/v1",
});

const resp = await openai.chat.completions.create({
  model: "ai/smollm2:360M-Q4_K_M",
  messages: [{ role: "user", content: "One haiku about containers." }],
});
console.log(resp.choices[0].message?.content);
```

### Gradio (load_chat)
```python
import gradio as gr
demo = gr.load_chat(
    "http://localhost:12434/engines/v1",
    model="ai/smollm2:360M-Q4_K_M",
    api_key="sk-local-123"
)
demo.launch()
```

You can omit `/llama.cpp` in the path (`/engines/v1/...`) per docs.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

### LangChain (example concept)

Point the client's base URL to `http://localhost:12434/engines/v1` and set the model to the DMR model name (e.g., `ai/smollm2:360M-Q4_K_M`). DMR's blog quickstart shows similar SDK wiring (Java/LangChain4j's baseUrl + model).

[Docker](https://www.docker.com/blog/)

## 5) Models endpoint (discovery)

```bash
# List models
curl http://localhost:12434/engines/v1/models

# Retrieve a model
curl http://localhost:12434/engines/v1/models/ai/smollm2
```

Paths are OpenAI-compatible under `/engines/v1/models`. Fully qualified variant is `/engines/llama.cpp/v1/models`.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

## 6) Embeddings & legacy completions

```bash
# Embeddings
curl http://localhost:12434/engines/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"ai/smollm2:360M-Q4_K_M","input":"hello world"}'

# Text completions (non-chat)
curl http://localhost:12434/engines/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"ai/smollm2:360M-Q4_K_M","prompt":"Write a tagline about Docker."}'
```

Supported endpoints listed in the API reference.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

## 7) Compose tips (calling from other containers)

```yaml
services:
  myapp:
    image: my/app
    extra_hosts:
      - "model-runner.docker.internal:host-gateway"
    environment:
      OPENAI_API_BASE: http://model-runner.docker.internal/engines/v1
      OPENAI_API_KEY: sk-local-123
```

Ensures your app can resolve the host gateway alias and hit DMR.

[Docker Documentation](https://docs.docker.com/compose/networking/)

## 8) Configure model limits (via Compose)

Use Models + Compose to set advanced parameters (e.g., max tokens, context). See "Models and Compose – Model configuration options" from the Get Started page.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/get-started/)

## 9) Troubleshooting checklist

- **"Connection refused"** → Enable host-side TCP in Docker Desktop (or use container URL).
  [Docker Documentation](https://docs.docker.com/desktop/model-runner/)

- **Browser frontend blocked** → Add your app's origin to CORS Allowed Origins in the AI settings.
  [Docker Documentation](https://docs.docker.com/desktop/model-runner/)

- **404 on model name** → Ensure you pulled the model and use the correct address (e.g., `ai/smollm2:360M-Q4_K_M`).
  [Docker Documentation](https://docs.docker.com/desktop/model-runner/get-started/)

- **From Compose container can't reach host** → add `extra_hosts: ["model-runner.docker.internal:host-gateway"]`.
  [Docker Documentation](https://docs.docker.com/compose/networking/)

- **Need socket instead of TCP** → use the `/exp/vDD4.40` prefix with the Docker socket path as per docs.
  [Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

## Handy one-liners

```bash
# Enable DMR with TCP on 12434 (Docker Desktop CLI)
docker desktop enable model-runner --tcp 12434
```

Matches the blog quickstart guidance for local SDKs.

[Docker](https://www.docker.com/blog/)

```bash
# Quick smoke test (host TCP)
curl http://localhost:12434/engines/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{"model":"ai/smollm2:360M-Q4_K_M","messages":[{"role":"user","content":"ping"}]}'
```

API path per DMR docs.

[Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

## Sources

- Docker blog quickstart on running LLMs locally with Model Runner (overview, endpoints, SDK idea).
  [Docker](https://www.docker.com/blog/)

- DMR Get Started (enablement, CORS, GPU, TCP, pull/run models, Compose config).
  [Docker Documentation](https://docs.docker.com/desktop/model-runner/)

- DMR REST API reference (base URLs, OpenAI-compatible endpoints, examples, socket path).
  [Docker Documentation](https://docs.docker.com/desktop/model-runner/api/)

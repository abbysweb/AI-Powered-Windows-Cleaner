# PHASE 15: ENHANCED AI CAPABILITIES - DETAILED IMPLEMENTATION PLAN

## Overview
Phase 15 enhances the AI advisor with three major capabilities: streaming token-by-token responses for improved UX, multi-modal reasoning for image analysis, and conversational memory for context-aware interactions.

## Phase Requirements

### Functional Requirements
| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-15.1 | Stream AI responses token-by-token | P0 | First token < 500ms, complete streaming without blocking UI |
| FR-15.2 | Support image analysis for error dialogs | P1 | Accept PNG/JPG, return structured analysis < 10s |
| FR-15.3 | Maintain conversation history across sessions | P1 | Context preserved across app restarts |
| FR-15.4 | Configurable model selection (llama3.2, llama3.1, code-llama) | P2 | Switch models without restart |

### Non-Functional Requirements
| ID | Requirement | Target |
|----|-------------|--------|
| NFR-15.1 | Streaming latency (first token) | < 500ms |
| NFR-15.2 | Image analysis response time | < 10s |
| NFR-15.3 | Memory retention duration | Configurable (default: 30 days) |
| NFR-15.4 | Test coverage | ≥ 95% |
| NFR-15.5 | Security scan | 0 critical/high issues |

## Architecture Design

### Component Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI CHAT WIDGET (GUI)                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Chat View    │  │ Image Upload │  │ Streaming Response View  │  │
│  │ (QTextEdit)  │  │ (QFileDialog)│  │ (QTextBrowser + Cursor)  │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬──────────────┘  │
│         │                 │                      │                 │
│         ▼                 ▼                      ▼                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    AI Chat Controller                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │ Conversation│  │ Image Proc. │  │ Streaming Handler   │  │  │
│  │  │ Manager     │  │ Service     │  │ (QThread + Signal)  │  │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │  │
│  └─────────┼────────────────┼─────────────────────┼─────────────┘  │
│            │                │                     │                │
└────────────┼────────────────┼─────────────────────┼────────────────┘
             │                │                     │
             ▼                ▼                     ▼
      ┌───────────────┐ ┌─────────────┐      ┌──────────────┐
      │  SQLite DB    │ │  Vision     │      │  FastAPI     │
      │  (History)    │ │  Model      │      │  Backend     │
      │               │ │  (LLaVA)    │      │  (Ollama)    │
      └───────────────┘ └─────────────┘      └──────────────┘
```

### Data Models

#### Conversation Memory Schema
```sql
-- Extended AIConversations table
ALTER TABLE AIConversations ADD COLUMN session_id TEXT;
ALTER TABLE AIConversations ADD COLUMN message_type TEXT DEFAULT 'text'; -- 'text' | 'image' | 'stream'
ALTER TABLE AIConversations ADD COLUMN token_count INTEGER DEFAULT 0;

-- New: Conversation Sessions
CREATE TABLE IF NOT EXISTS ConversationSessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    model TEXT NOT NULL DEFAULT 'llama3.2:1b',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- New: Image Analysis Results
CREATE TABLE IF NOT EXISTS ImageAnalyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    analysis_text TEXT NOT NULL,
    model_used TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ConversationSessions(id)
);
```

#### Streaming Protocol (FastAPI → GUI)
```python
# Server-Sent Events (SSE) format
data: {"type": "token", "content": "Hello", "done": false}\n\n
data: {"type": "token", "content": " world", "done": false}\n\n
data: {"type": "complete", "content": "", "done": true, "usage": {"prompt_tokens": 10, "completion_tokens": 5}}\n\n
```

### API Extensions

#### FastAPI Backend (New Endpoints)
```python
# Streaming chat
POST /api/chat/stream
{
    "session_id": "uuid",
    "messages": [{"role": "user", "content": "..."}],
    "model": "llama3.2:1b",
    "stream": true,
    "system_prompt": "...",
    "temperature": 0.7
}

# Image analysis (multi-modal)
POST /api/vision/analyze
{
    "image_base64": "...",
    "prompt": "Analyze this error dialog",
    "model": "llava:7b"
}

# Session management
GET /api/sessions
POST /api/sessions
GET /api/sessions/{id}
DELETE /api/sessions/{id}
GET /api/sessions/{id}/messages
```

## Implementation Plan

### Sprint 1: Streaming AI Responses (Week 1-2)

#### Backend Tasks
- [ ] Implement `/api/chat/stream` endpoint with SSE
- [ ] Add streaming support to Ollama client
- [ ] Handle cancellation and timeout
- [ ] Add token usage tracking

#### Frontend Tasks
- [ ] Create `StreamingResponseWidget` with token-by-token rendering
- [ ] Implement `StreamingWorker` (QThread) for SSE connection
- [ ] Add typing indicator during streaming
- [ ] Handle stream interruption/resumption

#### Integration Tests
- [ ] Test streaming with 100+ token responses
- [ ] Verify UI remains responsive during streaming
- [ ] Test cancellation mid-stream
- [ ] Validate token usage persistence

### Sprint 2: Multi-modal Reasoning (Week 2-3)

#### Backend Tasks
- [ ] Add LLaVA model support to Ollama container
- [ ] Implement `/api/vision/analyze` endpoint
- [ ] Add image preprocessing (resize, format conversion)
- [ ] Implement structured output parsing

#### Frontend Tasks
- [ ] Add image upload button to chat interface
- [ ] Create image preview thumbnail
- [ ] Implement drag-and-drop for screenshots
- [ ] Add "Analyze Error Dialog" quick action

#### Integration Tests
- [ ] Test PNG/JPG upload and analysis
- [ ] Verify error dialog detection accuracy
- [ ] Test large image handling (>5MB)
- [ ] Validate structured output format

### Sprint 3: Conversational Memory (Week 3-4)

#### Backend Tasks
- [ ] Implement session management API
- [ ] Add context window management (sliding window)
- [ ] Implement session persistence
- [ ] Add model-specific context limits

#### Frontend Tasks
- [ ] Create session sidebar/history panel
- [ ] Implement session switching
- [ ] Add session naming (auto-generated from first message)
- [ ] Implement "New Chat" button
- [ ] Add memory settings (retention period, max messages)

#### Integration Tests
- [ ] Test session persistence across app restarts
- [ ] Verify context window truncation
- [ ] Test multi-session isolation
- [ ] Validate memory settings enforcement

## Technical Specifications

### Streaming Implementation (Frontend)
```python
class StreamingWorker(QThread):
    token_received = Signal(str)  # partial token
    stream_complete = Signal(dict)  # usage stats
    error_occurred = Signal(str)
    
    def __init__(self, session_id: str, messages: list[dict]):
        super().__init__()
        self.session_id = session_id
        self.messages = messages
        self._cancelled = False
    
    def run(self):
        response = requests.post(
            f"{API_URL}/api/chat/stream",
            json={"session_id": self.session_id, "messages": self.messages, "stream": True},
            stream=True,
            timeout=30
        )
        for line in response.iter_lines():
            if self._cancelled:
                break
            if line:
                data = parse_sse(line)
                if data["type"] == "token":
                    self.token_received.emit(data["content"])
                elif data["type"] == "complete":
                    self.stream_complete.emit(data)
    
    def cancel(self):
        self._cancelled = True
```

### Image Analysis Implementation
```python
class VisionAnalysisService:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    def analyze_image(self, image_path: str, prompt: str) -> dict:
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        
        response = requests.post(
            f"{self.endpoint}/api/vision/analyze",
            json={
                "image_base64": image_b64,
                "prompt": prompt,
                "model": "llava:7b"
            },
            timeout=30
        )
        return response.json()
```

### Conversation Memory Manager
```python
class ConversationManager:
    def __init__(self, db_path: str):
        self.db = DatabaseManager(db_path)
        self.max_context_tokens = 4096  # model-dependent
    
    def create_session(self, model: str = "llama3.2:1b") -> str:
        session_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO ConversationSessions (id, model) VALUES (?, ?)",
            (session_id, model)
        )
        return session_id
    
    def get_context(self, session_id: str, max_tokens: int = None) -> list[dict]:
        messages = self.db.query(
            "SELECT role, content FROM AIConversations WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        return self._truncate_context(messages, max_tokens or self.max_context_tokens)
    
    def _truncate_context(self, messages: list[dict], max_tokens: int) -> list[dict]:
        # Implement sliding window with system prompt preservation
        total = sum(estimate_tokens(m["content"]) for m in messages)
        while total > max_tokens and len(messages) > 1:
            removed = messages.pop(1)  # Keep system prompt at index 0
            total -= estimate_tokens(removed["content"])
        return messages
```

## Testing Strategy

### Unit Tests
| Module | Test Cases |
|--------|------------|
| StreamingWorker | Token emission, cancellation, error handling, timeout |
| VisionAnalysisService | Base64 encoding, API formatting, response parsing |
| ConversationManager | Session CRUD, context truncation, token estimation |
| SSE Parser | Valid events, malformed data, completion detection |

### Integration Tests
| Scenario | Expected Result |
|----------|-----------------|
| Stream 500-token response | UI updates smoothly, no blocking |
| Upload 3MB screenshot | Analysis completes < 10s |
| Restart app with active session | Context restored, history visible |
| Switch models mid-conversation | Context preserved, model updated |
| Max context exceeded | Oldest messages truncated, system prompt kept |

### E2E Tests
```python
def test_full_streaming_flow():
    # 1. User sends message
    # 2. Streaming begins within 500ms
    # 3. Tokens appear in chat view
    # 4. Stream completes with usage stats
    # 5. Message persisted to database

def test_image_analysis_flow():
    # 1. User drags error screenshot
    # 2. Preview shown
    # 3. "Analyze" clicked
    # 4. Structured result returned
    # 5. Result added to conversation

def test_memory_persistence():
    # 1. Create session, exchange 5 messages
    # 2. Restart application
    # 3. Session appears in history
    # 4. Click session → context restored
    # 5. Continue conversation seamlessly
```

## Security Considerations

1. **Image Upload Validation**
   - Max file size: 10MB
   - Allowed formats: PNG, JPEG, WebP
   - Strip EXIF metadata
   - Validate magic bytes

2. **Streaming Security**
   - Rate limit: 30 req/min per session
   - Sanitize SSE output (prevent XSS)
   - Timeout: 60s max stream duration

3. **Memory Protection**
   - Encrypt sensitive conversation data at rest
   - Auto-delete sessions after retention period
   - Limit max sessions per user (default: 50)

## Performance Benchmarks

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| First token latency | N/A | < 500ms | p95 across 100 requests |
| Streaming throughput | N/A | > 50 tok/s | Sustained over 1000 tokens |
| Image analysis | N/A | < 10s | 2MB PNG, LLaVA 7B |
| Session restore | N/A | < 200ms | 50-message session |
| Context truncation | N/A | < 10ms | 4096 token window |

## Deployment Checklist

### Backend (Podman)
- [ ] Update `podman-compose.yml` with LLaVA model
- [ ] Add vision model volume
- [ ] Update FastAPI dependencies (`python-multipart`, `pillow`)
- [ ] Add new API routes and models
- [ ] Run database migrations

### Frontend
- [ ] Update requirements.txt (no new deps for streaming)
- [ ] Add image handling utilities
- [ ] Update chat UI with streaming view
- [ ] Add session management UI
- [ ] Update settings for memory configuration

### CI/CD
- [ ] Add streaming test to pytest suite
- [ ] Add vision test with sample images
- [ ] Add memory persistence test
- [ ] Update system_diagnosis.py for new components

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLaVA model too large for local hardware | Medium | High | Provide fallback to text-only; allow smaller models |
| Streaming SSE connection drops | Low | Medium | Implement reconnection with resume |
| Context window truncation loses critical info | Medium | Medium | Preserve system prompt + last N messages |
| Image analysis latency > 10s | Low | Low | Add progress indicator, allow async |

## Dependencies

### New Python Dependencies
```
# Backend
pillow>=10.0.0          # Image processing
python-multipart>=0.0.6 # Form data handling

# Frontend (already available)
# PySide6, requests, sqlite3 - no new deps needed
```

### New Container Images
```
ollama/ollama:latest     # Already present
llava:7b                 # New: ~4.7GB vision model
```

## Rollback Plan
If Phase 15 introduces regressions:
1. Disable streaming: Set `stream: false` in chat requests
2. Disable vision: Comment out `/api/vision/analyze` route
3. Disable memory: Set `max_context_tokens = 0`
4. Database migration is additive (no breaking schema changes)

## Success Criteria
- [ ] All unit tests pass (≥ 95% coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Security scan: 0 critical/high
- [ ] Performance benchmarks met
- [ ] System diagnosis: 100/100
- [ ] Documentation updated
- [ ] User acceptance testing passed

## Timeline Summary

| Sprint | Duration | Focus | Deliverable |
|--------|----------|-------|-------------|
| Sprint 1 | 2 weeks | Streaming Responses | Token-by-token chat |
| Sprint 2 | 2 weeks | Multi-modal Vision | Image analysis |
| Sprint 3 | 2 weeks | Conversational Memory | Persistent sessions |
| **Total** | **6 weeks** | **Phase 15 Complete** | **All 3 features** |

---

*Phase 15 Plan v1.0*  
*Author: Abdullah Al Mamun*  
*Date: 2026-08-04*
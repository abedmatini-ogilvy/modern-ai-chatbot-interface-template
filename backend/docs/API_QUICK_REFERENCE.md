# Research API Quick Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Start Research
```bash
POST /api/research/start
```

**Using Pre-configured Question:**
```json
{
  "question_id": "gen_z_nigeria",
  "conversation_id": "conv-123"
}
```

**Using Custom Question:**
```json
{
  "question": "Your research question here",
  "search_query": "search terms for APIs",
  "conversation_id": "conv-123",
  "max_results": 50
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Research started successfully",
  "question": "...",
  "search_query": "...",
  "status_url": "/api/research/{id}/status",
  "result_url": "/api/research/{id}/result"
}
```

---

### 2. Check Status
```bash
GET /api/research/{session_id}/status
```

**Response:**
```json
{
  "session_id": "uuid",
  "phase": "data_collection",
  "progress_percentage": 40,
  "current_agent": "Twitter Intelligence Agent",
  "progress_updates": [
    {
      "timestamp": "2024-01-01T12:00:00",
      "phase": "data_collection",
      "agent": "Twitter Intelligence Agent",
      "status": "completed",
      "message": "✅ Found 15 tweets"
    }
  ],
  "started_at": "2024-01-01T12:00:00",
  "estimated_completion": "2024-01-01T12:00:30"
}
```

**Phases:**
- `pending` → `data_collection` → `analysis` → `report_generation` → `completed`
- `failed` (if error occurs)

---

### 3. Get Result
```bash
GET /api/research/{session_id}/result
```

**Response:**
```json
{
  "session_id": "uuid",
  "question": "...",
  "search_query": "...",
  "phase": "completed",
  "started_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:00:30",
  "execution_time_seconds": 8.5,
  "data_collected": {
    "social_media": {
      "twitter": {"total_results": 15},
      "tiktok": {"total_results": 50},
      "reddit": {"total_results": 50}
    },
    "trends": {
      "search_volume_index": 51,
      "trending_status": "Steady"
    },
    "web_intelligence": {"total_results": 50}
  },
  "total_data_points": 166,
  "failed_apis": [],
  "insights": "Detailed analysis here",
  "report": "Full markdown report here",
  "executive_summary": "Summary here",
  "key_findings": ["Finding 1", "Finding 2"],
  "recommendations": ["Rec 1", "Rec 2"]
}
```

---

### 4. List Questions
```bash
GET /api/research/questions
```

**Response:**
```json
[
  {
    "id": "gen_z_nigeria",
    "title": "Gen Z Nigeria: Facebook vs Google Usage",
    "question": "Why does Gen Z in Nigeria...",
    "focus": "Social behavior patterns...",
    "search_terms": ["Gen Z Nigeria Facebook", "..."]
  }
]
```

---

### 5. List Sessions
```bash
GET /api/research/sessions
GET /api/research/sessions?conversation_id=conv-123
GET /api/research/sessions?phase=completed
```

**Response:**
```json
[
  {
    "session_id": "uuid",
    "question": "...",
    "search_query": "...",
    "conversation_id": "conv-123",
    "phase": "completed",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:30",
    "progress_count": 18,
    "has_result": true
  }
]
```

---

### 6. Delete Session
```bash
DELETE /api/research/{session_id}
```

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

---

### 7. Get Statistics
```bash
GET /api/research/statistics
```

**Response:**
```json
{
  "total_sessions": 5,
  "max_sessions": 100,
  "by_phase": {
    "pending": 1,
    "data_collection": 2,
    "completed": 2
  },
  "capacity_percentage": 5.0
}
```

---

## Testing with curl

### Complete Research Flow
```bash
# 1. Start research
RESPONSE=$(curl -s -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"question_id": "gen_z_nigeria", "conversation_id": "test-001"}')

SESSION_ID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo "Session ID: $SESSION_ID"

# 2. Poll status (repeat every 3 seconds)
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/research/$SESSION_ID/status")
  PHASE=$(echo $STATUS | python -c "import sys, json; print(json.load(sys.stdin)['phase'])")
  PROGRESS=$(echo $STATUS | python -c "import sys, json; print(json.load(sys.stdin)['progress_percentage'])")
  
  echo "Phase: $PHASE, Progress: $PROGRESS%"
  
  if [ "$PHASE" = "completed" ] || [ "$PHASE" = "failed" ]; then
    break
  fi
  
  sleep 3
done

# 3. Get result
curl -s "http://localhost:8000/api/research/$SESSION_ID/result" | python -m json.tool
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Either 'question' or 'question_id' must be provided",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00"
}
```

### 404 Not Found
```json
{
  "error": "Session not found",
  "status_code": 404,
  "timestamp": "2024-01-01T12:00:00"
}
```

### 503 Service Unavailable
```json
{
  "error": "Server at capacity. Please try again later.",
  "status_code": 503,
  "timestamp": "2024-01-01T12:00:00"
}
```

---

## Frontend Integration Pattern

```typescript
// Start research
const { session_id } = await fetch('/api/research/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question_id: 'gen_z_nigeria',
    conversation_id: currentConversationId
  })
}).then(r => r.json());

// Poll for progress
const pollInterval = setInterval(async () => {
  const status = await fetch(`/api/research/${session_id}/status`).then(r => r.json());
  
  // Update UI with progress
  updateProgressBar(status.progress_percentage);
  displayProgressUpdates(status.progress_updates);
  
  // Check if complete
  if (status.phase === 'completed') {
    clearInterval(pollInterval);
    
    // Get final result
    const result = await fetch(`/api/research/${session_id}/result`).then(r => r.json());
    displayReport(result);
  }
}, 3000); // Poll every 3 seconds
```

---

## Available Research Questions

1. **gen_z_nigeria** - Gen Z Nigeria: Facebook vs Google Usage
2. **detty_december** - Detty December Tourism Analysis  
3. **creator_economy** - African Creator Economy Challenges
4. **edtech_adoption** - Education Technology Adoption Patterns

---

## Documentation URLs

- **Interactive Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

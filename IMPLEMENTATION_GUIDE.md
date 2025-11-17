# LangGraph Chat Threads & Document Isolation Implementation Guide

## Overview
This implementation adds the following features to your LLM-PKG application:

### 1. **LangGraph Chat Threads with Memory**
- Each conversation has a unique `thread_id` for maintaining context across messages
- LangGraph's `MemorySaver` enables conversation continuity
- Chat history is preserved and used in subsequent queries

### 2. **Document Isolation**
- **Per User**: Documents are isolated by user_id
- **Per Conversation**: Documents can be linked to specific conversations
- Documents without conversation_id are available to all conversations for that user
- Conversation-specific documents take priority in RAG retrieval

### 3. **AI Agent Mode**
- When no documents are available, the system automatically switches to AI agent mode
- Provides intelligent responses using the LLM's general knowledge
- Clearly indicates when information is not from documents

### 4. **Collapsible UI**
- Chat history sidebar can be collapsed/expanded
- Collapsed view shows conversation icons
- Smooth transitions and responsive design
- Document upload section integrated in sidebar

## Database Changes

### New Columns
1. **conversations.thread_id** - LangGraph thread identifier (unique, indexed)
2. **documents.conversation_id** - Links documents to specific conversations (optional)

### New Table
- **conversation_documents** - Junction table for many-to-many relationship between conversations and documents

## Migration Steps

### 1. Run Database Migration
```bash
# If using Docker
docker-compose exec app alembic upgrade head

# If running locally
python -m alembic upgrade head
```

### 2. Install Additional Dependencies
The following dependencies are already in pyproject.toml:
- `langgraph==1.0.3` (with checkpoint.memory for MemorySaver)
- `langchain==1.0.3`
- `langchain-openai>=0.3.33`

### 3. Frontend Build
```bash
cd frontend
npm install
npm run build
```

## API Changes

### New Endpoints

#### 1. Upload Document (Conversation-Specific)
```
POST /chat/upload-document
Content-Type: multipart/form-data

Fields:
- file: File
- conversation_id: Optional[int]

Response:
{
  "message": "Document uploaded successfully",
  "document_id": 123,
  "filename": "example.pdf",
  "conversation_id": 456,
  "scope": "conversation" | "user"
}
```

#### 2. List Documents
```
GET /chat/documents?conversation_id={id}

Response:
[
  {
    "id": 123,
    "filename": "example.pdf",
    "conversation_id": 456,
    "created_at": "2025-11-17T10:30:00",
    "scope": "conversation" | "user"
  }
]
```

### Modified Endpoints

#### Chat Send Message
Now includes:
- Automatic thread_id generation for new conversations
- Conversation-specific document retrieval
- AI agent mode fallback
- Enhanced metadata in responses

```json
{
  "conversation_id": 123,
  "answer": "...",
  "sources": [...],
  "metadata": {
    "mode": "rag" | "agent",
    "num_sources": 3,
    "context_length": 1500
  }
}
```

## Usage Examples

### 1. Upload User-Wide Document
```python
# Available to all conversations for this user
POST /chat/upload-document
{
  "file": <file_data>
}
```

### 2. Upload Conversation-Specific Document
```python
# Only available to specific conversation
POST /chat/upload-document
{
  "file": <file_data>,
  "conversation_id": 123
}
```

### 3. Query with Context
```python
# Automatically uses:
# 1. Conversation-specific documents (priority)
# 2. User-wide documents
# 3. AI agent mode if no documents

POST /chat/send
{
  "message": "What is the main topic?",
  "conversation_id": 123
}
```

## Frontend Changes

### Collapsible Sidebar
- Click the chevron button to collapse/expand
- Collapsed view shows conversation icons (first 2 letters of title)
- Smooth CSS transitions

### Document Upload
- Upload documents from the sidebar
- Optionally link to current conversation
- View document scope (user vs conversation)

## Configuration

### Environment Variables
Ensure these are set:
```bash
DATABASE_URL=postgresql://user:password@postgres:5432/llm_pkg
OPENAI_API_KEY=your_openai_api_key
STORAGE_DIR=/app/data/uploads  # or ./data/uploads for local
```

### LangGraph Settings
The QA engine automatically:
- Creates thread IDs for conversations
- Maintains conversation state using MemorySaver
- Handles context window limits
- Provides graceful fallbacks

## Testing

### Test Document Isolation
```bash
# 1. Login as User A, create conversation, upload document
# 2. Login as User B, create conversation - should NOT see User A's docs
# 3. User A creates new conversation - should see user-wide docs but not conversation-specific ones from other conversations
```

### Test AI Agent Mode
```bash
# 1. Create conversation without uploading documents
# 2. Ask a question
# 3. Should receive AI-generated response with metadata.mode = "agent"
```

### Test Thread Continuity
```bash
# 1. Send message: "My name is John"
# 2. Send message: "What is my name?"
# 3. Should respond with "John" using conversation history
```

## Troubleshooting

### Migration Issues
If migration fails:
```bash
# Check current migration state
alembic current

# Manually run the migration
alembic upgrade add_thread_docs_001
```

### No Documents Retrieved
- Check user_id matches in documents table
- Verify conversation_id is correctly set
- Check STORAGE_DIR permissions

### Memory Not Working
- Ensure MemorySaver is properly initialized
- Check thread_id is consistent across requests
- Verify LangGraph version >= 1.0.3

## Performance Considerations

### Vector Store
- Documents are chunked (1000 chars, 200 overlap)
- Similarity search limited to k=3 most relevant chunks
- Priority ordering: conversation docs > user docs

### Database Queries
- Indexed on user_id, conversation_id, thread_id
- Efficient vector similarity using pgvector
- Proper foreign key constraints for data integrity

## Security

### Document Isolation
- Documents are strictly isolated by user_id
- Conversation ownership verified on all operations
- No cross-user document access possible

### Authentication
- All endpoints require valid JWT token
- User context automatically injected
- Conversation ownership enforced

## Future Enhancements

Potential improvements:
1. Document embedding caching
2. Conversation export/import
3. Advanced RAG strategies (hybrid search, re-ranking)
4. Document previews in UI
5. Batch document upload
6. Document versioning
7. Conversation sharing (with permissions)

## Support

For issues or questions:
1. Check logs: `docker-compose logs app`
2. Verify database state: `docker-compose exec postgres psql -U user -d llm_pkg`
3. Test API endpoints: `/docs` (FastAPI Swagger UI)

---

**Implementation Date**: November 17, 2025
**Version**: 0.2.0


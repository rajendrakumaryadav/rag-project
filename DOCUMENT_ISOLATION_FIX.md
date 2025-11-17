# Document Isolation Fix - Conversation-Specific Documents

## Summary
Fixed the issue where documents were being shared across all chat sessions. Documents are now strictly isolated to the specific conversation they were uploaded to.

## Changes Made

### Backend Changes

#### 1. `src/llm_pkg/qa_engine.py`
**Changed:** Document loading logic to enforce strict conversation isolation
- **Before:** Documents uploaded to a conversation OR user-wide documents (conversation_id = NULL) were available to all conversations
- **After:** Only documents uploaded to the specific conversation are loaded
```python
# OLD - allowed cross-conversation access
query = query.filter(
    (DBDocument.conversation_id == self.conversation_id) |
    (DBDocument.conversation_id == None)
)

# NEW - strict isolation
if self.conversation_id:
    query = query.filter(DBDocument.conversation_id == self.conversation_id)
else:
    query = query.filter(DBDocument.conversation_id == None)
```

#### 2. `src/llm_pkg/storage.py`
**Changed:** Vector store similarity search to only search conversation-specific documents
- **Before:** Searched both conversation-specific and user-wide documents
- **After:** Only searches documents belonging to the specific conversation
```python
# OLD - allowed cross-conversation access
AND (conversation_id = :conversation_id OR conversation_id IS NULL)

# NEW - strict isolation
AND conversation_id = :conversation_id
```

#### 3. `src/llm_pkg/chat_router.py`
**Changed:** Upload and list endpoints to require conversation_id
- **upload_document endpoint:** Changed `conversation_id` from `Optional[int]` to required `int`
- **list_user_documents endpoint:** Changed `conversation_id` from optional to required parameter
- Documents can no longer be uploaded without specifying a conversation
- Documents are always scoped to a conversation (scope='conversation')

### Frontend Changes

#### 4. `frontend/src/api/client.ts`
**Changed:** API client methods to require conversation_id
```typescript
// OLD - optional conversationId
uploadDocument: async (file: File, conversationId?: number)
listChatDocuments: async (conversationId?: number)

// NEW - required conversationId
uploadDocument: async (file: File, conversationId: number)
listChatDocuments: async (conversationId: number)
```

#### 5. `frontend/src/components/chat/DocumentUpload.tsx`
**Changed:** Complete rewrite to require active conversation
- Added `conversationId` as required prop
- Upload button is disabled when no conversation is selected
- Documents are automatically loaded/cleared when conversation changes
- Shows message "Select Conversation" when no conversation is active
- Removed delete functionality (documents are now conversation-scoped)
- Uses `chatAPI` instead of `documentAPI`

#### 6. `frontend/src/components/chat/Chat.tsx`
**Changed:** Pass current conversation ID to DocumentUpload
```tsx
// NEW - passes conversationId
<DocumentUpload 
  conversationId={currentConversation?.id || null} 
  onUploadComplete={loadConversations} 
/>
```

## Behavior

### Before Fix
- ❌ Documents uploaded to Conversation A were visible in Conversation B, C, D, etc.
- ❌ All users' documents within their account were available across all conversations
- ❌ No proper document isolation between chat sessions

### After Fix
- ✅ Documents uploaded to Conversation A are ONLY visible in Conversation A
- ✅ Each conversation has its own isolated document set
- ✅ Users must select/create a conversation before uploading documents
- ✅ Documents are automatically filtered by conversation_id in all queries
- ✅ Vector search only retrieves embeddings from the current conversation

## User Experience

1. **Starting a new conversation:**
   - Upload button shows "Select Conversation" and is disabled
   - User must start a conversation first

2. **Uploading a document:**
   - User selects or creates a conversation
   - Upload button becomes active
   - Document is uploaded and linked to the current conversation
   - Document is only accessible within that conversation

3. **Switching conversations:**
   - Documents list automatically updates to show only documents for the selected conversation
   - Previous conversation's documents are no longer visible
   - Queries only search within the current conversation's documents

4. **Asking questions:**
   - RAG (Retrieval-Augmented Generation) only uses documents from the current conversation
   - No cross-contamination of information between different conversations
   - Each conversation maintains its own context

## Database Schema
The existing schema already supported this with:
- `documents.conversation_id` - Foreign key to link document to conversation
- `ConversationDocument` - Many-to-many relationship table (for future enhancements)

## Migration Notes
- No database migration required (schema already supported this)
- Existing documents without conversation_id will only be accessible in "no conversation" context
- Consider running a cleanup script if needed to associate orphaned documents

## Testing Recommendations
1. Create Conversation A, upload document "test1.pdf"
2. Create Conversation B, upload document "test2.pdf"
3. Switch to Conversation A, verify only "test1.pdf" is visible
4. Ask questions in Conversation A, verify answers only reference "test1.pdf"
5. Switch to Conversation B, verify only "test2.pdf" is visible
6. Ask questions in Conversation B, verify answers only reference "test2.pdf"

## Benefits
- ✅ **Privacy:** Documents are isolated per conversation
- ✅ **Context Clarity:** Each conversation has clear, relevant context
- ✅ **No Cross-Talk:** Prevents information leakage between different topics/conversations
- ✅ **Better UX:** Users know exactly which documents are being used for each conversation
- ✅ **Scalability:** Better performance as vector searches are scoped to smaller document sets


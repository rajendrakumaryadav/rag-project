# Document Isolation Architecture

## Before Fix - Documents Shared Across Conversations ❌

```
User Account
├── Conversation A
│   ├── Messages
│   └── Can access: ALL documents (A, B, C)
│
├── Conversation B
│   ├── Messages
│   └── Can access: ALL documents (A, B, C)
│
└── Documents Pool (SHARED)
    ├── Document A (conversation_id = 1 OR NULL)
    ├── Document B (conversation_id = 2 OR NULL)
    └── Document C (conversation_id = NULL)
```

**Problem:** 
- Document uploaded to Conversation A was visible in Conversation B
- Document queries included: `conversation_id = X OR conversation_id = NULL`
- No proper isolation between chat sessions

---

## After Fix - Strict Conversation Isolation ✅

```
User Account
│
├── Conversation A
│   ├── Messages
│   └── Documents (ISOLATED)
│       └── Document A (conversation_id = 1)
│
├── Conversation B
│   ├── Messages
│   └── Documents (ISOLATED)
│       └── Document B (conversation_id = 2)
│
└── Conversation C
    ├── Messages
    └── Documents (ISOLATED)
        └── Document C (conversation_id = 3)
```

**Solution:**
- Each conversation has its own isolated document set
- Document queries filter: `conversation_id = X` (strict equality)
- No cross-contamination between conversations

---

## Data Flow - Document Upload

### Before Fix
```
User uploads document
        ↓
Frontend sends file + conversation_id (optional)
        ↓
Backend saves with conversation_id OR NULL
        ↓
Document available to ALL user's conversations ❌
```

### After Fix
```
User selects conversation (required)
        ↓
User uploads document
        ↓
Frontend sends file + conversation_id (required)
        ↓
Backend saves with conversation_id (required)
        ↓
Document ONLY available to that conversation ✅
```

---

## Query Flow - RAG (Retrieval-Augmented Generation)

### Before Fix
```
User asks question in Conversation A
        ↓
QA Engine loads documents WHERE:
  user_id = X AND (conversation_id = A OR conversation_id IS NULL)
        ↓
Vector search across ALL user documents
        ↓
Answer may reference documents from other conversations ❌
```

### After Fix
```
User asks question in Conversation A
        ↓
QA Engine loads documents WHERE:
  user_id = X AND conversation_id = A
        ↓
Vector search ONLY within Conversation A documents
        ↓
Answer references ONLY Conversation A documents ✅
```

---

## Database Queries

### Before Fix - Document Loading
```sql
SELECT * FROM documents 
WHERE user_id = ? 
AND (conversation_id = ? OR conversation_id IS NULL)
-- ❌ Returns documents from multiple conversations
```

### After Fix - Document Loading
```sql
SELECT * FROM documents 
WHERE user_id = ? 
AND conversation_id = ?
-- ✅ Returns ONLY documents from current conversation
```

### Before Fix - Vector Similarity Search
```sql
SELECT id, filename, content,
       1 - (embedding <=> ?) as similarity
FROM documents
WHERE embedding IS NOT NULL
AND user_id = ?
AND (conversation_id = ? OR conversation_id IS NULL)
ORDER BY embedding <=> ?
LIMIT ?
-- ❌ Searches across all user documents
```

### After Fix - Vector Similarity Search
```sql
SELECT id, filename, content,
       1 - (embedding <=> ?) as similarity
FROM documents
WHERE embedding IS NOT NULL
AND user_id = ?
AND conversation_id = ?
ORDER BY embedding <=> ?
LIMIT ?
-- ✅ Searches only within conversation documents
```

---

## Frontend Component States

### DocumentUpload Component

#### State 1: No Conversation Selected
```
┌─────────────────────────────┐
│  [Upload: DISABLED]         │
│  "Select Conversation"      │
└─────────────────────────────┘
```

#### State 2: Conversation Selected
```
┌─────────────────────────────┐
│  [Upload Document: ENABLED] │
│  "Upload Document"          │
│                             │
│  [View Documents (3)]       │
└─────────────────────────────┘
```

#### State 3: Viewing Documents
```
┌─────────────────────────────┐
│  [Upload Document]          │
│                             │
│  [Hide Documents (3)]       │
│  ┌─────────────────────┐   │
│  │ 📄 doc1.pdf         │   │
│  │    conversation • ... │  │
│  ├─────────────────────┤   │
│  │ 📄 doc2.txt         │   │
│  │    conversation • ... │  │
│  └─────────────────────┘   │
└─────────────────────────────┘
```

---

## API Changes Summary

### Backend Endpoints

| Endpoint | Parameter | Before | After |
|----------|-----------|--------|-------|
| `/chat/upload-document` | conversation_id | Optional | **Required** |
| `/chat/documents` | conversation_id | Optional | **Required** |

### Frontend API Client

| Method | Signature Before | Signature After |
|--------|-----------------|-----------------|
| `uploadDocument` | `(file, conversationId?)` | `(file, conversationId)` |
| `listChatDocuments` | `(conversationId?)` | `(conversationId)` |

### Frontend Component Props

| Component | Prop | Before | After |
|-----------|------|--------|-------|
| `DocumentUpload` | conversationId | N/A | **Required** `number \| null` |

---

## Security & Privacy Benefits

1. **Data Isolation**
   - Documents cannot leak between conversations
   - Each conversation maintains its own knowledge base

2. **Context Clarity**
   - Users know exactly which documents are active
   - No confusion about which sources are being referenced

3. **Performance**
   - Smaller document sets per conversation
   - Faster vector searches (scoped to conversation)
   - Reduced embedding search space

4. **Compliance**
   - Better data segmentation
   - Easier to manage document lifecycle per conversation
   - Clear audit trail (document → conversation relationship)

---

## Migration Path

### For Existing Documents

```sql
-- Find orphaned documents (no conversation_id)
SELECT COUNT(*) FROM documents WHERE conversation_id IS NULL;

-- Option 1: Delete orphaned documents
DELETE FROM documents WHERE conversation_id IS NULL;

-- Option 2: Associate with a default conversation (if needed)
UPDATE documents 
SET conversation_id = (
    SELECT id FROM conversations 
    WHERE user_id = documents.user_id 
    ORDER BY created_at DESC 
    LIMIT 1
)
WHERE conversation_id IS NULL;
```

### Rollback Plan (if needed)

To revert to previous behavior:

1. Make conversation_id optional in endpoints
2. Update queries to include `OR conversation_id IS NULL`
3. Update frontend to make conversationId optional

---

## Testing Checklist

- [ ] Upload document without conversation → Should fail
- [ ] Upload document to Conversation A → Success
- [ ] Upload document to Conversation B → Success
- [ ] View documents in Conversation A → Only see A's documents
- [ ] View documents in Conversation B → Only see B's documents
- [ ] Ask question in Conversation A → References only A's documents
- [ ] Ask question in Conversation B → References only B's documents
- [ ] Switch between conversations → Document list updates correctly
- [ ] Create new conversation → Starts with empty document set
- [ ] Delete conversation → Documents are also removed (cascade)

---

## Performance Considerations

### Before Fix
- Vector search dimension: **All user documents** (potentially 100s-1000s)
- Query complexity: O(n) where n = total user documents
- Cache invalidation: Global (affects all conversations)

### After Fix
- Vector search dimension: **Current conversation documents** (typically 1-10)
- Query complexity: O(n) where n = conversation documents (much smaller)
- Cache invalidation: Per-conversation (isolated)

**Result:** Significant performance improvement for users with many documents across multiple conversations.


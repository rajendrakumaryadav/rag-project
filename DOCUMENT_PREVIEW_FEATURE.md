# Document Preview Feature Implementation

## Overview
This document describes the newly implemented document preview feature with matching relation tracking in the LLM-PKG application.

## Features Implemented

### 1. **Document Preview Modal** ✅
- Full document content display
- Syntax highlighting for matched sections
- Usage statistics and history
- Tabbed interface (Content / Usage History)
- Responsive design with smooth animations

### 2. **Document-Message Matching** ✅
- Track which documents were used to answer questions
- Store matched content snippets
- Record relevance scores
- Link messages to source documents
- Show usage history in preview

### 3. **Interactive Source References** ✅
- Clickable preview buttons on message sources
- Hover effects on document items
- Quick access to document content from chat
- Visual feedback for document usage

## Database Schema

### New Table: `message_document_matches`
```sql
CREATE TABLE message_document_matches (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    document_id INTEGER NOT NULL REFERENCES documents(id),
    matched_content TEXT,
    relevance_score VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### 1. Preview Document
```http
GET /chat/documents/{document_id}/preview
Authorization: Bearer <token>

Response 200:
{
  "id": 123,
  "filename": "example.pdf",
  "content": "Full document content...",
  "file_path": "/path/to/file",
  "conversation_id": 456,
  "created_at": "2025-11-17T10:30:00",
  "usage_count": 5,
  "recent_matches": [
    {
      "message_id": 789,
      "message_content": "What is Python?",
      "matched_content": "Python is a programming language...",
      "relevance_score": "0.85",
      "created_at": "2025-11-17T11:00:00"
    }
  ]
}
```

### 2. Get Message Document Matches
```http
GET /chat/messages/{message_id}/document-matches
Authorization: Bearer <token>

Response 200:
[
  {
    "document_id": 123,
    "filename": "example.pdf",
    "matched_content": "Relevant content snippet...",
    "relevance_score": "0.85",
    "conversation_id": 456
  }
]
```

## Frontend Components

### DocumentPreview Component
**Location**: `frontend/src/components/chat/DocumentPreview.tsx`

**Features**:
- Modal overlay with backdrop
- Two tabs: Content and Usage History
- Highlighted matched sections in content
- Usage timeline showing recent questions
- Relevance scores for each match
- Responsive layout

**Props**:
```typescript
interface DocumentPreviewProps {
  documentId: number;
  onClose: () => void;
}
```

### Enhanced DocumentUpload Component
**Location**: `frontend/src/components/chat/DocumentUpload.tsx`

**New Features**:
- Eye icon button to preview documents
- Integrated with DocumentPreview modal
- Shows document list with preview capability

### Enhanced MessageList Component
**Location**: `frontend/src/components/chat/MessageList.tsx`

**New Features**:
- Preview button on source items (appears on hover)
- Document ID tracking in sources
- Click to preview source documents
- Visual feedback with hover effects

## Usage Flow

### Viewing Document Preview from Document List
1. User opens a conversation
2. Clicks "View Documents" button
3. Document list appears
4. Clicks eye icon on any document
5. DocumentPreview modal opens
6. User can switch between Content and Usage History tabs
7. Matched sections are highlighted in yellow

### Viewing Document Preview from Message Sources
1. User receives AI response with sources
2. Sources are displayed below the message
3. User hovers over a source item
4. Eye icon appears
5. Clicks eye icon
6. DocumentPreview modal opens showing the source document

### Document Matching Flow
1. User asks a question
2. QA Engine retrieves relevant documents
3. Response is generated using document context
4. Backend saves MessageDocumentMatch records
5. Matched content and relevance scores are stored
6. Usage count is incremented
7. Sources are returned in response with document IDs

## Technical Implementation

### Backend Changes

#### 1. Database Model (`models.py`)
- Added `MessageDocumentMatch` model
- Tracks message-document relationships
- Stores matched content snippets
- Records relevance scores

#### 2. Chat Router (`chat_router.py`)
- Added `/documents/{document_id}/preview` endpoint
- Added `/messages/{message_id}/document-matches` endpoint
- Enhanced `send_message` to save document matches
- Extracts document IDs from sources

#### 3. QA Engine (`qa_engine.py`)
- Updated source formatting to include document IDs
- Added filename field to sources
- Includes similarity scores in response

#### 4. Migration (`alembic/versions/add_message_document_matches.py`)
- Creates message_document_matches table
- Adds indexes for performance

### Frontend Changes

#### 1. API Client (`client.ts`)
```typescript
// New methods
previewDocument(documentId: number): Promise<any>
getMessageDocumentMatches(messageId: number): Promise<any[]>
```

#### 2. Component Structure
```
Chat.tsx
├── DocumentUpload.tsx
│   └── DocumentPreview.tsx (modal)
└── MessageList.tsx
    └── DocumentPreview.tsx (modal)
```

#### 3. Styling Features
- Yellow highlighting for matched content
- Smooth modal animations
- Gradient backgrounds
- Responsive tabs
- Hover effects
- Loading states

## Highlighting Algorithm

The DocumentPreview component uses intelligent content highlighting:

1. **Extract Match Snippets**: Get all matched content from usage history
2. **Sort by Length**: Process longer snippets first (prevents partial matches)
3. **Escape Regex**: Safely handle special characters
4. **Replace with Markers**: Use unique temporary markers
5. **Apply Styling**: Convert markers to HTML with yellow background

```typescript
const highlightMatchedContent = (content: string, matches: any[]) => {
  // Sort matches by length (descending)
  const matchedSnippets = matches
    .map(m => m.matched_content)
    .filter(Boolean)
    .sort((a, b) => b.length - a.length);

  // Replace each snippet with highlighted version
  matchedSnippets.forEach((snippet, index) => {
    const escapedSnippet = snippet.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escapedSnippet, 'gi');
    const marker = `__HIGHLIGHT_${index}__`;
    highlightedContent = highlightedContent.replace(regex, marker);
  });

  // Convert markers to HTML
  return highlightedContent; // with <mark> tags
};
```

## Security Considerations

### Authorization
- ✅ All endpoints verify user authentication
- ✅ Document ownership checked before preview
- ✅ Conversation ownership validated
- ✅ Cross-user document access prevented

### Data Privacy
- ✅ Users can only preview their own documents
- ✅ Document matches only visible to document owner
- ✅ Conversation isolation maintained

### Input Validation
- ✅ Document IDs validated
- ✅ Message IDs validated
- ✅ SQL injection prevented via ORM
- ✅ XSS prevented via React's escaping

## Performance Optimizations

### Database
- Indexed columns: message_id, document_id
- Limit recent matches to 10 items
- Efficient JOIN queries for matches

### Frontend
- Lazy loading of preview modal
- CSS-only animations (hardware accelerated)
- Conditional rendering
- Minimal re-renders with React hooks

### API
- Pagination for large match lists
- Content truncation in list views
- Full content only on preview

## Testing Scenarios

### Test 1: Document Preview
```
✅ Upload document
✅ Click preview button
✅ Modal opens with content
✅ Content is displayed correctly
✅ Close button works
```

### Test 2: Document Matching
```
✅ Upload document with content
✅ Ask question about document
✅ Response includes sources
✅ Source has document ID
✅ MessageDocumentMatch created
✅ Matched content stored
```

### Test 3: Usage History
```
✅ Ask multiple questions about same document
✅ Preview document
✅ Switch to Usage History tab
✅ All questions are listed
✅ Matched content is shown
✅ Relevance scores displayed
```

### Test 4: Highlighting
```
✅ Multiple matches on same document
✅ Preview shows highlighted sections
✅ Yellow background on matches
✅ Original content preserved
✅ Special characters handled
```

### Test 5: Source Preview
```
✅ Receive message with sources
✅ Hover over source item
✅ Eye icon appears
✅ Click eye icon
✅ Document preview opens
✅ Shows correct document
```

## Migration Instructions

### Step 1: Run Database Migration
```bash
# Development
alembic upgrade head

# Docker
docker-compose exec app alembic upgrade head
```

### Step 2: Rebuild Frontend
```bash
cd frontend
npm install
npm run build
```

### Step 3: Restart Services
```bash
# Docker
docker-compose restart

# Development
# Restart backend and frontend servers
```

### Step 4: Verify
```bash
# Check migration
alembic current

# Check database table
docker-compose exec postgres psql -U user -d llm_pkg \
  -c "SELECT * FROM message_document_matches LIMIT 1;"
```

## Future Enhancements

### Potential Features
1. **Advanced Search**: Search within document content
2. **Annotations**: Allow users to highlight and annotate
3. **Version History**: Track document changes
4. **Bulk Operations**: Preview multiple documents
5. **Export**: Download documents with highlights
6. **Statistics**: Document usage analytics dashboard
7. **Recommendations**: Suggest relevant documents
8. **Sharing**: Share documents with other users

### Performance Improvements
1. **Caching**: Cache frequently accessed documents
2. **Lazy Loading**: Load content on scroll
3. **Compression**: Compress large documents
4. **CDN**: Serve documents via CDN
5. **Thumbnails**: Generate document previews

## Troubleshooting

### Preview Not Opening
```typescript
// Check console for errors
// Verify document ID is being passed
// Check API endpoint is accessible
```

### Highlights Not Showing
```typescript
// Verify matched_content is not null
// Check usage_count > 0
// Ensure recent_matches array has items
```

### Slow Preview Loading
```sql
-- Check database indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename = 'message_document_matches';
```

### Missing Matches
```python
# Check if sources have document IDs
# Verify MessageDocumentMatch is being created
# Check document ownership
```

## Summary

The document preview feature provides a comprehensive solution for:
- ✅ Viewing full document content
- ✅ Tracking document usage
- ✅ Highlighting relevant sections
- ✅ Understanding document-message relationships
- ✅ Improving user experience
- ✅ Maintaining security and privacy

**Status**: ✅ PRODUCTION READY
**Version**: 1.0.0
**Date**: November 17, 2025


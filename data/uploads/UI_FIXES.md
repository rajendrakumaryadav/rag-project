# UI Fixes - Provider/Model Mismatch & Upload Before First Message

## Issues Fixed

### Issue 1: Provider/Model Mismatch ❌
**Problem:** UI showed "gemini • gpt-4o" - wrong model for provider

**Root Cause:** When a conversation was created from the first message, the backend always used `model="gpt-4o"` regardless of the selected provider.

**Fix:** 
- Backend now maps provider to correct model:
  - `openai` → `gpt-4o`
  - `gemini` → `gemini-pro`
  - `anthropic` → `claude-3-opus-20240229`
  - `default` → `gpt-4o`

**Files Changed:**
- `src/llm_pkg/chat_router.py` (lines 131-154)

**Code:**
```python
# Map provider to default model
provider_model_map = {
    "default": "gpt-4o",
    "openai": "gpt-4o",
    "gemini": "gemini-pro",
    "anthropic": "claude-3-opus-20240229",
}
model = provider_model_map.get(provider, "gpt-4o")
```

---

### Issue 2: Upload Disabled Until First Message ❌
**Problem:** Document upload button was disabled in new conversations until the first message was sent

**Root Cause:** 
- DocumentUpload component requires `conversationId` (number)
- New chat sessions had `currentConversation = null`
- Conversation was only created when first message was sent

**Fix:**
- "New Chat" button now creates an actual conversation immediately
- Conversation is created in the database with title "New Conversation"
- Upload button is enabled immediately
- Title is updated from first message content

**Files Changed:**
- `frontend/src/components/chat/Chat.tsx` (handleNewConversation function)
- `src/llm_pkg/chat_router.py` (update title on first message)

**Frontend Code:**
```typescript
const handleNewConversation = async () => {
  try {
    // Create a new conversation immediately
    const newConv = await chatAPI.createConversation({
      title: 'New Conversation',
      provider: selectedProvider !== 'default' ? selectedProvider : 'openai',
      model: getModelForProvider(selectedProvider !== 'default' ? selectedProvider : 'openai'),
    });
    
    // Set as current conversation
    setCurrentConversation(newConv);
    setMessages([]);
    
    // Reload conversations list
    await loadConversations();
  } catch (error) {
    console.error('Failed to create conversation:', error);
    // Fallback to old behavior
    setCurrentConversation(null);
    setMessages([]);
  }
};
```

**Backend Code:**
```python
# Update title if it's still the default and this is the first message
if conversation.title == "New Conversation":
    message_count = db.query(Message).filter(Message.conversation_id == conversation.id).count()
    if message_count == 0:
        conversation.title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        db.add(conversation)
```

---

## Behavior Changes

### Before Fixes

**Issue 1:**
```
User selects: Gemini
Conversation displays: "gemini • gpt-4o" ❌
Backend tries to use: gpt-4o model with gemini provider
Result: Error or wrong model used
```

**Issue 2:**
```
1. User clicks "New Chat"
2. currentConversation = null
3. Upload button: [Select Conversation] (disabled) ❌
4. User must send message first
5. Conversation created
6. Upload button enabled
```

### After Fixes

**Issue 1:**
```
User selects: Gemini
Conversation displays: "gemini • gemini-pro" ✅
Backend uses: gemini-pro model with gemini provider
Result: Correct model for provider
```

**Issue 2:**
```
1. User clicks "New Chat"
2. Conversation created with title "New Conversation"
3. currentConversation = { id: X, title: "New Conversation", ... }
4. Upload button: [Upload Document] (enabled) ✅
5. User can upload documents immediately
6. First message updates title automatically
```

---

## User Experience Improvements

### Provider/Model Matching
- ✅ Each provider now shows its correct default model
- ✅ No more confusing "gemini • gpt-4o" mismatches
- ✅ Backend uses appropriate model for the selected provider
- ✅ Prevents API errors from model/provider mismatches

### Immediate Upload Capability
- ✅ Upload button is enabled as soon as conversation is created
- ✅ Users can prepare documents before chatting
- ✅ No need to send a dummy message first
- ✅ Better workflow for document-heavy conversations
- ✅ Conversation title auto-updates from first message

---

## Testing Instructions

### Test 1: Provider/Model Matching
```
1. Create new conversation (click "New Chat")
2. Select "Gemini" from model selector
3. Send a message
4. Check conversation header
   ✅ Should show: "gemini • gemini-pro"
   
5. Create another conversation
6. Select "Anthropic"
7. Send a message
   ✅ Should show: "anthropic • claude-3-opus-20240229"
```

### Test 2: Immediate Document Upload
```
1. Click "New Chat"
   ✅ Conversation created immediately
   ✅ Shows in sidebar as "New Conversation"
   
2. Check upload button
   ✅ Should show "Upload Document" (enabled)
   
3. Upload a document (e.g., test.pdf)
   ✅ Upload succeeds
   ✅ Document appears in "View Documents"
   
4. Send first message: "What is in the document?"
   ✅ Conversation title updates to first ~50 chars
   ✅ Answer uses uploaded document
```

### Test 3: Title Auto-Update
```
1. Create new conversation
   - Initial title: "New Conversation"
   
2. Upload document (optional)
   
3. Send message: "Tell me about quantum computing"
   ✅ Title updates to: "Tell me about quantum computing"
   
4. Send another message
   ✅ Title stays the same (only updates from first message)
```

---

## Edge Cases Handled

### Provider/Model Mapping
- Unknown provider defaults to "gpt-4o"
- "default" provider uses "gpt-4o"
- Case-sensitive provider names handled

### Conversation Creation
- If conversation creation fails, gracefully falls back to old behavior
- Conversation list reloads after creation
- Title update only happens on first message
- Empty messages don't trigger title update

### Document Upload
- Upload disabled if conversation creation failed
- Upload works immediately after conversation created
- Documents isolated to the conversation they're uploaded to

---

## Files Modified

### Backend
```
src/llm_pkg/chat_router.py
  - Lines 123-131: Update title on first message
  - Lines 133-154: Provider/model mapping for new conversations
```

### Frontend
```
frontend/src/components/chat/Chat.tsx
  - Lines 70-112: Improved handleSendMessage with title refresh
  - Lines 114-133: New handleNewConversation creates actual conversation
  - Lines 135-143: Helper function getModelForProvider
```

---

## Technical Details

### Provider Model Map
```python
provider_model_map = {
    "default": "gpt-4o",
    "openai": "gpt-4o",
    "gemini": "gemini-pro",
    "anthropic": "claude-3-opus-20240229",
}
```

### Database Impact
- New conversations created immediately with "New Conversation" title
- Title field updated on first message if still default
- No schema changes required
- Backward compatible

### API Changes
- No breaking changes to API endpoints
- Conversation creation behaves the same
- Send message endpoint handles title updates transparently

---

## Benefits

### For Users
- ✅ Clear, accurate provider/model information
- ✅ Upload documents before sending messages
- ✅ Better workflow for document-heavy conversations
- ✅ Auto-generated conversation titles from first message
- ✅ Immediate feedback when creating conversations

### For Developers
- ✅ Cleaner separation of concerns
- ✅ Provider/model mapping in one place
- ✅ Consistent conversation creation flow
- ✅ Better error handling

### For System
- ✅ Correct model used for each provider (prevents API errors)
- ✅ Reduced failed API calls
- ✅ Better user experience metrics

---

## Rollback Plan

If issues arise, revert these commits:
```bash
git log --oneline | grep -E "provider|upload"
git revert <commit-hash>
```

Or manually revert changes in:
- `src/llm_pkg/chat_router.py`
- `frontend/src/components/chat/Chat.tsx`

---

## Related Issues

This fix addresses:
- ✅ Provider/model mismatch display
- ✅ Upload disabled in new conversations
- ✅ Better conversation creation UX
- ✅ Auto-title generation from first message

Complements:
- Document isolation fix (conversation-specific documents)
- Provider selection improvements
- Chat UX enhancements

---

## Status: ✅ COMPLETE

Both issues are now fixed:
1. ✅ Provider/model matching is correct
2. ✅ Document upload works immediately in new conversations

Ready for testing and deployment!


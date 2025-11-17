# Document Preview - Quick Reference Guide

## 🚀 Quick Start

### Viewing Document Previews

#### Method 1: From Document List
1. Open a conversation
2. Click **"View Documents"** button
3. Click the **eye icon** (👁️) on any document
4. Preview modal opens

#### Method 2: From Message Sources
1. Ask a question that uses documents
2. AI responds with sources shown below
3. Hover over any source item
4. Click the **eye icon** that appears
5. Preview modal opens

## 📑 Preview Modal Features

### Content Tab
- **Full Document**: Shows complete document text
- **Highlighted Sections**: Yellow highlights show content that was used to answer questions
- **Readable Format**: Monospace font with proper formatting
- **Info Banner**: Explains highlighting when matches exist

### Usage History Tab
- **Question List**: All questions answered using this document
- **Matched Content**: Specific snippets that were relevant
- **Relevance Scores**: How well content matched the question
- **Timestamps**: When each question was asked
- **Question Preview**: First 100 characters of each question

## 🎯 Key Features

### Visual Indicators
- **Yellow Highlights**: Content used in answers
- **Gradient Icons**: Document type indicators
- **Badge Counts**: Number of times document was referenced
- **Hover Effects**: Interactive elements respond to mouse

### Information Displayed
```
Header:
├── Document filename
├── Upload timestamp
└── Total references count

Content Tab:
├── Full document text
├── Highlighted matches
└── Formatting preserved

Usage Tab:
├── Recent questions (up to 10)
├── Matched content snippets
├── Relevance scores
└── Question timestamps
```

## 💡 Usage Tips

### Understanding Highlights
- **Yellow Background**: Content was used to answer a question
- **Multiple Highlights**: Document answered multiple questions
- **No Highlights**: Document hasn't been used yet OR currently viewing Usage tab

### Relevance Scores
- **0.0 - 0.3**: Low relevance (might be background info)
- **0.3 - 0.7**: Medium relevance (supporting information)
- **0.7 - 1.0**: High relevance (directly answers question)

### Best Practices
1. **Upload Clear Documents**: Well-formatted documents highlight better
2. **Ask Specific Questions**: Get more precise matches
3. **Check Usage History**: Understand how documents are being used
4. **Preview Before Deleting**: Review usage before removing documents

## 🔍 Finding Information

### In Content Tab
1. Use browser search (Ctrl+F / Cmd+F)
2. Look for yellow highlights first
3. Scroll through full content
4. Click outside to close

### In Usage Tab
1. Review recent questions
2. Check matched content
3. Identify patterns
4. Click outside to close

## ⚡ Keyboard Shortcuts

- **Esc**: Close preview modal
- **Click Outside**: Close preview modal
- **Tab**: Navigate between tabs

## 🎨 UI Elements

### Document List Item
```
┌─────────────────────────────────────┐
│ [📄] example.pdf              [👁️] │
│ conversation • Nov 17, 2025         │
└─────────────────────────────────────┘
```

### Message Source Item
```
┌─────────────────────────────────────┐
│ 🔗 example.pdf              [👁️]   │
│ Page 1                              │
│ "Content snippet from doc..."       │
└─────────────────────────────────────┘
```

### Preview Modal
```
┌───────────────────────────────────────┐
│ 📄 example.pdf                    [✕] │
│ 🕐 Nov 17, 2025  •  🔗 5 references   │
├───────────────────────────────────────┤
│ [Content] [Usage History (5)]         │
├───────────────────────────────────────┤
│                                       │
│   Document content with               │
│   yellow highlighted sections         │
│   showing matched content...          │
│                                       │
├───────────────────────────────────────┤
│                          [Close]      │
└───────────────────────────────────────┘
```

## 📊 Understanding Metrics

### Usage Count
- Shows total times document was referenced
- Appears in header as "X references"
- Zero means document uploaded but not used yet

### Matched Content
- First 200 characters shown in sources
- Full snippets in preview modal
- Highlighting shows exact matches

### Relevance Score
- Calculated by vector similarity
- Range: 0.0 (no match) to 1.0 (perfect match)
- Higher = more relevant to question

## 🔒 Privacy & Security

### What You Can See
- ✅ Your own documents
- ✅ Your conversation documents
- ✅ Your usage history

### What You Cannot See
- ❌ Other users' documents
- ❌ Other users' questions
- ❌ Cross-conversation data (isolated)

## 🐛 Troubleshooting

### Preview Won't Open
- **Check**: Document ID exists
- **Verify**: You own the document
- **Try**: Refresh the page

### No Highlights Visible
- **Reason**: Document hasn't been used yet
- **Solution**: Ask questions about the document
- **Check**: Switch to Usage History tab to verify

### Slow Loading
- **Cause**: Large document size
- **Solution**: Wait a few seconds
- **Tip**: Use smaller documents when possible

### Missing Sources
- **Reason**: Question didn't use documents
- **Check**: AI used agent mode instead of RAG
- **Solution**: Upload relevant documents first

## 🎓 Example Workflow

### Complete Usage Example

```
1. Upload Document
   ├── Click "Upload Document"
   ├── Select "python_guide.pdf"
   └── Wait for confirmation

2. Ask Questions
   ├── "What is a list comprehension?"
   ├── "How do I use decorators?"
   └── "Explain generators"

3. View Preview
   ├── Click "View Documents"
   ├── Find "python_guide.pdf"
   ├── Click eye icon
   └── Modal opens

4. Explore Content
   ├── Content Tab: See highlighted sections
   ├── Usage Tab: See 3 questions
   ├── Review matched content
   └── Check relevance scores

5. Close Modal
   ├── Click [Close] button
   ├── Or click outside modal
   └── Or press Esc key
```

## 📱 Responsive Design

### Desktop (> 768px)
- Full-width modal (max 4xl)
- Two-column layouts where applicable
- Smooth hover effects

### Tablet (768px - 1024px)
- Adjusted modal width
- Single-column layouts
- Touch-friendly buttons

### Mobile (< 768px)
- Full-screen modals
- Stacked layouts
- Larger touch targets

## 🚦 Status Indicators

### Colors
- **Blue**: Information, links
- **Green/Emerald**: Documents, success
- **Yellow**: Highlights, warnings
- **Red**: Errors, deletion
- **Gray**: Neutral, inactive

### Icons
- **📄 FileText**: Documents
- **👁️ Eye**: Preview action
- **🔗 Link2**: References
- **🕐 Clock**: Timestamps
- **📈 TrendingUp**: Usage statistics
- **✕ X**: Close action

## 💻 Developer Notes

### API Calls
```typescript
// Preview document
const doc = await chatAPI.previewDocument(documentId);

// Get message matches
const matches = await chatAPI.getMessageDocumentMatches(messageId);
```

### Component Props
```typescript
<DocumentPreview 
  documentId={123} 
  onClose={() => setPreviewDocumentId(null)} 
/>
```

## 📞 Need Help?

### Common Questions

**Q: Can I preview documents before uploading?**
A: Not yet - preview works after upload. Future enhancement!

**Q: Can I edit documents in preview?**
A: No - preview is read-only. Download and re-upload to update.

**Q: How long is usage history kept?**
A: Forever! All matches are stored permanently.

**Q: Can I export highlighted documents?**
A: Not yet - future enhancement planned.

---

**Last Updated**: November 17, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready


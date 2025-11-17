"""
Chat API endpoints.
Handles conversations, messages, and LLM interactions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from llm_pkg.auth.utils import get_current_active_user
from llm_pkg.database.models import Conversation, Message, User, get_db, Document as DBDocument
from llm_pkg.qa_engine import QAEngine

router = APIRouter(prefix="/chat", tags=["chat"])


class ConversationCreate(BaseModel):
    title: str
    provider: str = "default"
    model: str = "gpt-4o"


class ConversationResponse(BaseModel):
    id: int
    title: str
    provider: str
    model: str
    created_at: str
    updated_at: str


class MessageCreate(BaseModel):
    content: str
    provider: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str


class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = None
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
    answer: str
    sources: List[dict]


def get_qa_engine(user: User = Depends(get_current_active_user)) -> QAEngine:
    """Get QA engine instance for the current user."""
    # Create user-specific QA engine instance
    from llm_pkg.config import graph_manager, llm_loader
    
    return QAEngine(llm_loader, graph_manager, user_id=user.id)


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(conv: ConversationCreate, current_user: User = Depends(get_current_active_user),
                              db: Session = Depends(get_db), ):
    """Create a new conversation."""
    db_conv = Conversation(user_id=current_user.id, title=conv.title, provider=conv.provider, model=conv.model, )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    
    return ConversationResponse(id=db_conv.id, title=db_conv.title, provider=db_conv.provider, model=db_conv.model,
                                created_at=db_conv.created_at.isoformat(), updated_at=db_conv.updated_at.isoformat(), )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """List user's conversations."""
    conversations = (db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(
        Conversation.updated_at.desc()).all())
    
    return [ConversationResponse(id=conv.id, title=conv.title, provider=conv.provider, model=conv.model,
                                 created_at=conv.created_at.isoformat(),
                                 updated_at=conv.updated_at.isoformat() if conv.updated_at else conv.created_at.isoformat(), )
            for conv in conversations]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: int, current_user: User = Depends(get_current_active_user),
                                    db: Session = Depends(get_db), ):
    """Get messages for a conversation."""
    # Verify conversation ownership
    conversation = (db.query(Conversation).filter(Conversation.id == conversation_id,
                                                  Conversation.user_id == current_user.id).first())
    
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    messages = (db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all())
    
    return [MessageResponse(id=msg.id, conversation_id=msg.conversation_id, role=msg.role, content=msg.content,
                            created_at=msg.created_at.isoformat(), ) for msg in messages]


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest, current_user: User = Depends(get_current_active_user),
                       db: Session = Depends(get_db), ):
    """Send a message and get AI response."""
    import logging
    import uuid
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = (db.query(Conversation).filter(Conversation.id == request.conversation_id,
                                                          Conversation.user_id == current_user.id, ).first())
            if not conversation:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found", )
        else:
            # Create new conversation with thread_id
            thread_id = str(uuid.uuid4())
            conversation = Conversation(user_id=current_user.id, title=request.message[:50] + "..." if len(
                request.message) > 50 else request.message, provider=request.provider or "default", model="gpt-4o",
                                        # Default model
                                        thread_id=thread_id, )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save user message
        user_msg = Message(conversation_id=conversation.id, role="user", content=request.message, )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        
        # Get QA engine with conversation-specific context
        from llm_pkg.config import graph_manager, llm_loader
        
        qa_engine = QAEngine(llm_loader, graph_manager, user_id=current_user.id, conversation_id=conversation.id)
        
        # Use RAG with thread ID for conversation continuity
        sources = []
        try:
            # Use RAG-enabled query method with thread ID
            result = await qa_engine.query(request.message, request.provider, thread_id=conversation.thread_id)
            answer = result["answer"]
            sources = result.get("sources", [])
            metadata = result.get("metadata", {})
            
            # Log the mode being used
            mode = metadata.get("mode", "unknown")
            logger.info(f"Query mode: {mode}, Sources: {len(sources)}")
        
        except Exception as e:
            logger.warning(f"RAG query failed, falling back to simple query: {e}")
            try:
                # Fallback to simple query without RAG
                answer = await qa_engine.query_simple(request.message, request.provider)
            except Exception as e2:
                logger.exception("Both RAG and simple query failed")
                answer = f"I apologize, but I encountered an error: {str(e2)}"
        
        # Save assistant message
        assistant_msg = Message(conversation_id=conversation.id, role="assistant", content=answer, )
        db.add(assistant_msg)
        
        # Update conversation timestamp
        conversation.updated_at = assistant_msg.created_at
        db.commit()
        db.refresh(assistant_msg)
        
        return ChatResponse(conversation_id=conversation.id,
                            user_message=MessageResponse(id=user_msg.id, conversation_id=user_msg.conversation_id,
                                                         role=user_msg.role, content=user_msg.content,
                                                         created_at=user_msg.created_at.isoformat(), ),
                            assistant_message=MessageResponse(id=assistant_msg.id,
                                                              conversation_id=assistant_msg.conversation_id,
                                                              role=assistant_msg.role, content=assistant_msg.content,
                                                              created_at=assistant_msg.created_at.isoformat(), ),
                            answer=answer, sources=sources, )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in send_message endpoint")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to process message: {str(e)}", )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_active_user),
                              db: Session = Depends(get_db), ):
    """Delete a conversation."""
    conversation = (db.query(Conversation).filter(Conversation.id == conversation_id,
                                                  Conversation.user_id == current_user.id).first())
    
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...), conversation_id: Optional[int] = Form(None),
                          current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db), ):
    """
    Upload a document for the current user, optionally linked to a conversation.
    Documents can be user-wide or conversation-specific.
    """
    import logging
    from llm_pkg.storage import STORAGE_DIR
    from llm_pkg.document_processor import DocumentProcessor
    
    logger = logging.getLogger(__name__)
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Verify conversation ownership if provided
        if conversation_id:
            conversation = (db.query(Conversation).filter(Conversation.id == conversation_id,
                                                          Conversation.user_id == current_user.id, ).first())
            if not conversation:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found", )
        
        # Read file content
        content = await file.read()
        
        # Save to storage
        file_path = STORAGE_DIR / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as f:
            f.write(content)
        
        # Process document
        doc_processor = DocumentProcessor()
        processed_data = await doc_processor.process_document(file_path)
        
        # Save to database
        db_doc = DBDocument(filename=file.filename,
                            content=processed_data.get("text", content.decode("utf-8", errors="ignore")),
                            file_path=str(file_path), user_id=current_user.id, conversation_id=conversation_id, )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        logger.info(f"Document uploaded: {file.filename} for user {current_user.id}, conversation {conversation_id}")
        
        return {"message": "Document uploaded successfully", "document_id": db_doc.id, "filename": file.filename,
                "conversation_id": conversation_id, "scope": "conversation" if conversation_id else "user", }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error uploading document")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to upload document: {str(e)}", )


@router.get("/documents")
async def list_user_documents(conversation_id: Optional[int] = None,
                              current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db), ):
    """List documents for the current user, optionally filtered by conversation."""
    query = db.query(DBDocument).filter(DBDocument.user_id == current_user.id)
    
    if conversation_id:
        # Verify conversation ownership
        conversation = (db.query(Conversation).filter(Conversation.id == conversation_id,
                                                      Conversation.user_id == current_user.id, ).first())
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found", )
        query = query.filter(DBDocument.conversation_id == conversation_id)
    
    documents = query.all()
    
    return [{"id": doc.id, "filename": doc.filename, "conversation_id": doc.conversation_id,
             "created_at": doc.created_at.isoformat(), "scope": "conversation" if doc.conversation_id else "user", } for
            doc in documents]

"""
QA Engine - LangChain & LangGraph Integration
==============================================
Implements question-answering using LangChain and LangGraph with RAG and memory.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
import uuid

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

from llm_pkg.config import LangGraphManager, LLMLoader
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.storage import PostgreSQLVectorStore

logger = logging.getLogger("llm_pkg.qa_engine")


class QAState(dict):
    """State for LangGraph QA workflow."""

    question: str
    chat_history: list
    documents: list[Document]
    context: str
    answer: str
    provider: str
    metadata: dict[str, Any]
    thread_id: str


class QAEngine:
    """
    Question-Answering engine using LangChain and LangGraph.
    Implements RAG (Retrieval-Augmented Generation) pattern with memory.
    """

    def __init__(
        self,
        llm_loader: LLMLoader,
        graph_manager: LangGraphManager,
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
    ):
        self.llm_loader = llm_loader
        self.graph_manager = graph_manager
        self.doc_processor = DocumentProcessor()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.vector_store = None
        
        # Memory saver for LangGraph
        self.memory = MemorySaver()
        self.qa_graph = self._build_qa_graph()

        # Optional: token encoding library to validate token counts
        try:
            import tiktoken
            self._tiktoken = tiktoken
        except Exception:
            self._tiktoken = None

    def _build_qa_graph(self) -> CompiledStateGraph:
        """Build LangGraph workflow for QA with memory."""
        workflow = StateGraph(dict)

        # Define nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        # Compile with memory checkpointer
        return workflow.compile(checkpointer=self.memory)

    async def _retrieve_node(self, state: dict) -> dict:
        """Retrieve relevant documents."""
        question = state["question"]
        document_name = state.get("document_name")

        logger.info(f"Retrieving documents for: {question[:50]}...")

        # Load and process documents (user and conversation specific)
        documents = await self._load_documents(document_name)

        # If no documents found, mark for AI agent mode
        if not documents:
            logger.info("No documents found, using AI agent mode")
            state["documents"] = []
            state["context"] = ""
            state["use_agent_mode"] = True
            return state

        # Split documents
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")

        try:
            # Create or update vector store with OpenAI embeddings
            embeddings = OpenAIEmbeddings()
            self.vector_store = PostgreSQLVectorStore(
                embeddings,
                user_id=self.user_id,
                conversation_id=self.conversation_id
            )

            # Add documents to vector store
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            self.vector_store.add_texts(texts, metadatas)

            # Retrieve relevant chunks - use k=10 to get chunks from multiple documents
            # This ensures we use all uploaded documents, not just one
            k_value = min(10, len(chunks))  # Don't request more chunks than we have
            relevant_docs = self.vector_store.similarity_search(question, k=k_value)
        except Exception as e:
            logger.warning(f"Vector store failed, using all document chunks: {e}")
            # Fallback: use first few chunks directly
            k_value = min(10, len(chunks))
            relevant_docs = chunks[:k_value]

        # Log which documents we're using
        doc_sources = set([doc.metadata.get("source", "unknown") for doc in relevant_docs])
        logger.info(f"Using {len(relevant_docs)} chunks from {len(doc_sources)} document(s): {doc_sources}")

        # Create context
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        state["documents"] = relevant_docs
        state["context"] = context
        state["use_agent_mode"] = False

        return state

    async def _generate_node(self, state: dict) -> dict:
        """Generate answer using LLM with conversation history."""
        question = state["question"]
        context = state["context"]
        provider = state.get("provider")
        chat_history = state.get("chat_history", [])
        use_agent_mode = state.get("use_agent_mode", False)

        logger.info(f"Generating answer using provider: {provider or 'default'}")

        # Build LLM
        llm = self.llm_loader.build_model(provider)

        # Create prompt based on mode
        if use_agent_mode:
            # AI Agent mode - no context, just conversation
            prompt = f"""You are a helpful AI assistant. Answer the user's question directly using your general knowledge and the conversation history if available.

DO NOT ask the user to upload or paste any documents or files. If the user references a specific file that is not available, say that you don't have access to the file and answer from your general knowledge instead.

Question: {question}

Answer:"""
        else:
            # RAG mode - use context from documents (possibly multiple documents)
            docs_in_context = state.get("documents", [])
            doc_sources = set([doc.metadata.get("source", "unknown") for doc in docs_in_context])
            
            prompt = f"""You are an AI assistant helping the user with their question based on the uploaded documents.

I have provided context from {len(doc_sources)} document(s): {', '.join(doc_sources)}

Please analyze ALL the provided context carefully and answer the question. Synthesize information from multiple documents if relevant. If the information is spread across different documents, combine them in your answer.

Context from uploaded documents:
{context}

Question: {question}

Instructions:
- Use the context above to answer the question thoroughly
- If information is found in the documents, cite which document(s) you're referencing
- If the context doesn't fully answer the question, use your general knowledge to supplement
- DO NOT ask the user to upload additional documents
- Provide a clear, comprehensive answer

Answer:"""

        # Add chat history for context if available
        if chat_history:
            history_text = "\n".join([
                f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                for msg in chat_history[-6:]  # Last 3 exchanges
            ])
            prompt = f"Previous conversation:\n{history_text}\n\n{prompt}"

        # Generate answer
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)

        # If the model responds by asking the user to provide document contents (common when the user explicitly asks for the contents of a specific file),
        # then automatically fallback to a strict general-knowledge response so the UI receives a useful answer instead of a request for upload.
        answer_lower = answer.lower() if isinstance(answer, str) else ""
        ask_for_upload_signals = [
            "please provide",
            "please paste",
            "i need the text",
            "provide the content",
            "upload the",
            "send the",
            "paste the",
            "can't access files",
            "i don't have access to",
        ]
        if any(sig in answer_lower for sig in ask_for_upload_signals):
            logger.info("LLM asked for document content; running strict general-knowledge fallback")
            fallback_prompt = f"You are a helpful AI assistant. The user asked: {question}\n\nAnswer directly using your general knowledge. Do NOT ask the user to upload or paste any documents or files. If you don't know, give the best possible general answer."
            try:
                fallback_resp = llm.invoke(fallback_prompt)
                fallback_answer = fallback_resp.content if hasattr(fallback_resp, "content") else str(fallback_resp)
                # If fallback produced something different, use it
                if fallback_answer and fallback_answer.strip():
                    answer = fallback_answer
            except Exception as e:
                logger.warning(f"Fallback general-knowledge LLM call failed: {e}")

        state["answer"] = answer
        state["metadata"] = {
            "num_sources": len(state.get("documents", [])),
            "context_length": len(context),
            "mode": "agent" if use_agent_mode else "rag",
        }

        return state

    async def _load_documents(self, document_name: str | None = None) -> list[Document]:
        """Load and process documents (user and conversation specific)."""
        from llm_pkg.database.models import get_db, Document as DBDocument
        from llm_pkg.storage import list_documents, read_document, STORAGE_DIR

        documents = []
        db = next(get_db())
        
        try:
            # Query documents for this user and conversation
            query = db.query(DBDocument).filter(DBDocument.user_id == self.user_id)
            
            if self.conversation_id:
                # Get ONLY conversation-specific documents (strict isolation)
                query = query.filter(DBDocument.conversation_id == self.conversation_id)
            else:
                # If no conversation_id, get only documents without a conversation
                query = query.filter(DBDocument.conversation_id == None)
            
            if document_name:
                query = query.filter(DBDocument.filename == document_name)
            
            db_docs = query.all()
            
            for db_doc in db_docs:
                doc = Document(
                    page_content=db_doc.content,
                    metadata={
                        "source": db_doc.filename,
                        "id": db_doc.id,
                        "conversation_id": db_doc.conversation_id,
                    }
                )
                documents.append(doc)
                
        finally:
            db.close()

        # If no documents were found in DB, try to load files directly from the storage directory
        if not documents:
            try:
                if STORAGE_DIR.exists():
                    for path in list_documents():
                        # Optionally filter by document_name
                        if document_name and path.name != document_name:
                            continue
                        try:
                            doc = read_document(path)
                            documents.append(doc)
                        except Exception as e:
                            logger.warning(f"Failed to read document from storage: {path}: {e}")
            except Exception as e:
                logger.warning(f"Error listing storage documents: {e}")

        logger.info(f"Loaded {len(documents)} document(s) for user {self.user_id}, conversation {self.conversation_id}")
        return documents

    async def query(
        self,
        question: str,
        provider: str | None = None,
        document_name: str | None = None,
        thread_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a question-answering query with memory.

        Args:
            question: The question to answer
            provider: Optional LLM provider to use
            document_name: Optional specific document to query
            thread_id: Thread ID for conversation continuity

        Returns:
            Dictionary with answer and metadata
        """
        # Generate or use provided thread ID
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        # Prepare initial state
        initial_state = {
            "question": question,
            "provider": provider,
            "document_name": document_name,
            "thread_id": thread_id,
            "documents": [],
            "context": "",
            "answer": "",
            "metadata": {},
            "chat_history": [],
        }

        # Execute LangGraph workflow with thread
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.qa_graph.ainvoke(initial_state, config)

        # Format response
        return {
            "answer": result["answer"],
            "sources": [
                {
                    "source": doc.metadata.get("source"),
                    "filename": doc.metadata.get("source"),
                    "id": doc.metadata.get("id"),
                    "page": doc.metadata.get("page"),
                    "content": doc.page_content[:200] + "...",
                    "similarity": doc.metadata.get("similarity"),
                }
                for doc in result.get("documents", [])
            ],
            "provider": provider or "default",
            "metadata": result.get("metadata", {}),
            "thread_id": thread_id,
        }

    async def query_simple(
        self,
        question: str,
        provider: str | None = None,
    ) -> str:
        """
        Simple query without RAG (direct LLM call).

        Args:
            question: The question to ask
            provider: Optional LLM provider to use

        Returns:
            Answer string
        """
        llm = self.llm_loader.build_model(provider)
        response = llm.invoke(question)
        return response.content if hasattr(response, "content") else str(response)

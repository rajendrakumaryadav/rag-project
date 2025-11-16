"""
QA Engine - LangChain & LangGraph Integration
==============================================
Implements question-answering using LangChain and LangGraph with RAG.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from llm_pkg.config import LangGraphManager, LLMLoader
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.storage import STORAGE_DIR, list_documents

logger = logging.getLogger("llm_pkg.qa_engine")


class QAState(dict):
    """State for LangGraph QA workflow."""

    question: str
    documents: list[Document]
    context: str
    answer: str
    provider: str
    metadata: dict[str, Any]


class QAEngine:
    """
    Question-Answering engine using LangChain and LangGraph.
    Implements RAG (Retrieval-Augmented Generation) pattern.
    """

    def __init__(self, llm_loader: LLMLoader, graph_manager: LangGraphManager):
        self.llm_loader = llm_loader
        self.graph_manager = graph_manager
        self.doc_processor = DocumentProcessor()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        self.vector_store = None
        self.qa_graph = self._build_qa_graph()

    def _build_qa_graph(self) -> CompiledStateGraph:
        """Build LangGraph workflow for QA."""
        workflow = StateGraph(dict)

        # Define nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    async def _retrieve_node(self, state: dict) -> dict:
        """Retrieve relevant documents."""
        question = state["question"]
        document_name = state.get("document_name")

        logger.info(f"Retrieving documents for: {question[:50]}...")

        # Load and process documents
        documents = await self._load_documents(document_name)

        # Split documents
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")

        # Create or update vector store
        embeddings = OpenAIEmbeddings()
        self.vector_store = FAISS.from_documents(chunks, embeddings)

        # Retrieve relevant chunks
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        relevant_docs = retriever.get_relevant_documents(question)

        # Create context
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        state["documents"] = relevant_docs
        state["context"] = context

        return state

    async def _generate_node(self, state: dict) -> dict:
        """Generate answer using LLM."""
        question = state["question"]
        context = state["context"]
        provider = state.get("provider")

        logger.info(f"Generating answer using provider: {provider or 'default'}")

        # Build LLM
        llm = self.llm_loader.build_model(provider)

        # Create prompt
        prompt = f"""Based on the following context, answer the question.
If you cannot find the answer in the context, say so.

Context:
{context}

Question: {question}

Answer:"""

        # Generate answer
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)

        state["answer"] = answer
        state["metadata"] = {
            "num_sources": len(state.get("documents", [])),
            "context_length": len(context),
        }

        return state

    async def _load_documents(self, document_name: str | None = None) -> list[Document]:
        """Load and process documents."""
        documents = []

        if document_name:
            # Load specific document
            file_path = STORAGE_DIR / document_name
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {document_name}")

            processed = await self.doc_processor.process_document(file_path)
            documents = self.doc_processor.create_langchain_documents(processed)
        else:
            # Load all documents
            for file_path in list_documents():
                if file_path.is_file():
                    try:
                        processed = await self.doc_processor.process_document(file_path)
                        docs = self.doc_processor.create_langchain_documents(processed)
                        documents.extend(docs)
                    except Exception as e:
                        logger.warning(f"Error processing {file_path.name}: {e}")

        logger.info(f"Loaded {len(documents)} document(s)")
        return documents

    async def query(
        self,
        question: str,
        provider: str | None = None,
        document_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a question-answering query.

        Args:
            question: The question to answer
            provider: Optional LLM provider to use
            document_name: Optional specific document to query

        Returns:
            Dictionary with answer and metadata
        """
        # Prepare initial state
        initial_state = {
            "question": question,
            "provider": provider,
            "document_name": document_name,
            "documents": [],
            "context": "",
            "answer": "",
            "metadata": {},
        }

        # Execute LangGraph workflow
        result = await self.qa_graph.ainvoke(initial_state)

        # Format response
        return {
            "answer": result["answer"],
            "sources": [
                {
                    "source": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "content": doc.page_content[:200] + "...",
                }
                for doc in result.get("documents", [])
            ],
            "provider": provider or "default",
            "metadata": result.get("metadata", {}),
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

"""
Example usage scripts for LLM-PKG
==================================
Demonstrates various ways to use the platform.
"""

import asyncio

from llm_pkg.config import graph_manager, llm_loader
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from llm_pkg.storage import save_document


async def example_1_upload_and_process():
    """Example 1: Upload and process a document."""
    print("=== Example 1: Upload and Process Document ===\n")

    # Create a sample document
    sample_text = """
    Machine Learning Research Paper
    
    Abstract:
    This paper presents a novel approach to natural language processing
    using transformer-based architectures. We demonstrate significant
    improvements in text classification tasks.
    
    Introduction:
    Natural Language Processing (NLP) has seen tremendous advances in
    recent years, particularly with the introduction of transformer models.
    
    Methodology:
    We used a BERT-based architecture with fine-tuning on domain-specific data.
    
    Results:
    Our model achieved 95% accuracy on the test set, outperforming baseline
    models by 10%.
    """

    # Save as a document
    file_path = save_document(sample_text.encode(), "sample_paper.txt")
    print(f"✓ Document saved: {file_path}")

    # Process the document
    processor = DocumentProcessor()
    processed = await processor.process_document(file_path)

    print("\n✓ Document processed:")
    print(f"  - Format: {processed['format']}")
    print(f"  - Words: {processed['summary']['total_words']}")
    print(f"  - Lines: {processed['summary']['total_lines']}")
    print(f"  - Headings: {processed['structure']['num_headings']}")


async def example_2_query_document():
    """Example 2: Query a document."""
    print("\n=== Example 2: Query Document ===\n")

    qa_engine = QAEngine(llm_loader, graph_manager)

    # Note: This requires valid API keys in config
    try:
        result = await qa_engine.query(
            question="What is the accuracy mentioned in the paper?",
            provider="openai",  # Change to your configured provider
        )

        print(f"Question: {result['question']}")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources: {len(result['sources'])} documents")
    except Exception as e:
        print(f"⚠ Query failed: {e}")
        print("Make sure to configure API keys in config/llm_config.toml")


async def example_3_multi_provider():
    """Example 3: Use multiple providers."""
    print("\n=== Example 3: Multiple Providers ===\n")

    # Show available providers
    print("Available providers:")
    for name, cfg in llm_loader.providers.items():
        print(f"  - {name}: {cfg.provider} ({cfg.model})")

    # Build models from different providers
    print("\nBuilding models:")
    for provider_name in ["openai", "azure", "ollama"]:
        try:
            model = llm_loader.build_model(provider_name)
            print(f"  ✓ {provider_name}: {type(model).__name__}")
        except Exception:
            print(f"  ✗ {provider_name}: Not configured")


async def example_4_langgraph_workflow():
    """Example 4: Custom LangGraph workflow."""
    print("\n=== Example 4: LangGraph Workflow ===\n")

    from langgraph.graph import END, StateGraph

    # Define a simple workflow
    workflow = StateGraph(dict)

    def step1(state):
        print("  → Step 1: Processing input")
        state["step1_done"] = True
        return state

    def step2(state):
        print("  → Step 2: Analyzing data")
        state["step2_done"] = True
        return state

    def step3(state):
        print("  → Step 3: Generating output")
        state["result"] = "Workflow completed!"
        return state

    workflow.add_node("step1", step1)
    workflow.add_node("step2", step2)
    workflow.add_node("step3", step3)

    workflow.set_entry_point("step1")
    workflow.add_edge("step1", "step2")
    workflow.add_edge("step2", "step3")
    workflow.add_edge("step3", END)

    graph = workflow.compile()

    # Execute workflow
    print("Executing workflow:")
    result = await graph.ainvoke({"input": "test"})
    print(f"\n✓ Result: {result['result']}")


async def example_5_batch_processing():
    """Example 5: Batch process multiple documents."""
    print("\n=== Example 5: Batch Processing ===\n")

    processor = DocumentProcessor()

    # Create sample documents
    documents = [
        ("doc1.txt", "First document about AI and machine learning."),
        ("doc2.txt", "Second document about data science and analytics."),
        ("doc3.txt", "Third document about deep learning and neural networks."),
    ]

    print(f"Processing {len(documents)} documents...")

    for filename, content in documents:
        file_path = save_document(content.encode(), filename)
        processed = await processor.process_document(file_path)
        print(f"  ✓ {filename}: {processed['summary']['total_words']} words")


async def main():
    """Run all examples."""
    print("LLM-PKG Examples")
    print("=" * 50)

    await example_1_upload_and_process()
    await example_2_query_document()
    await example_3_multi_provider()
    await example_4_langgraph_workflow()
    await example_5_batch_processing()

    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())

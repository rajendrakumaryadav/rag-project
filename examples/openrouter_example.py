#!/usr/bin/env python3
"""
Simple OpenRouter Example
Shows basic usage once you have credits
"""

import asyncio

from llm_pkg import QAEngine, graph_manager, llm_loader, save_document


async def example_simple_query():
    """Example 1: Simple direct query (no documents)"""
    print("=" * 60)
    print("Example 1: Simple Query (No Credits Needed for Testing)")
    print("=" * 60)

    qa_engine = QAEngine(llm_loader, graph_manager)

    # This will fail without credits, but shows the pattern
    try:
        result = await qa_engine.query_simple(
            question="What is 2+2?",
            provider="openrouter",  # or openrouter_claude, openrouter_llama, etc.
        )
        print(f"\nAnswer: {result}\n")
    except Exception as e:
        print(f"\nNote: {str(e)}")
        print("\n⚠️  You need to add credits at https://openrouter.ai/credits")
        print("   Minimum recommended: $5")
        print()


async def example_document_query():
    """Example 2: Document-based Q&A"""
    print("=" * 60)
    print("Example 2: Document Query with OpenRouter")
    print("=" * 60)

    # Create a sample document
    sample_doc = """
    Python Programming Basics
    
    Python is a high-level programming language known for its simplicity.
    Key features include:
    - Easy to read syntax
    - Dynamic typing
    - Extensive standard library
    - Large community support
    
    Common use cases: Web development, data science, automation, AI/ML
    """

    # Save the document
    doc_path = save_document(sample_doc.encode(), "python_basics.txt")
    print(f"✓ Created document: {doc_path.name}\n")

    # Query it with OpenRouter
    qa_engine = QAEngine(llm_loader, graph_manager)

    try:
        result = await qa_engine.query(
            question="What are the key features of Python?",
            provider="openrouter_llama",  # Using Llama (often cheaper)
            document_name="python_basics.txt",
        )

        print(f"Question: {result['question']}")
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources: {len(result['sources'])} document(s)")
        print()

    except Exception as e:
        print(f"\n⚠️  Error: {str(e)}")
        print("\nTo fix:")
        print("1. Visit https://openrouter.ai/credits")
        print("2. Add credits (minimum $5)")
        print("3. Run this script again")
        print()


def example_model_comparison():
    """Example 3: Compare different models"""
    print("=" * 60)
    print("Example 3: Model Comparison")
    print("=" * 60)

    models = [
        ("openrouter", "GPT-4o"),
        ("openrouter_claude", "Claude 3.5 Sonnet"),
        ("openrouter_llama", "Llama 3.1 70B"),
        ("openrouter_gemini", "Gemini Pro 1.5"),
    ]

    print("\nConfigured OpenRouter Models:")
    print("-" * 60)

    for provider, name in models:
        try:
            model = llm_loader.build_model(provider)
            config = llm_loader.get_provider_config(provider)
            print(f"✓ {provider:20} → {name:25} ({config.model})")
        except Exception as e:
            print(f"✗ {provider:20} → Error: {str(e)[:40]}")

    print()


async def example_with_temperature():
    """Example 4: Adjusting temperature for different tasks"""
    print("=" * 60)
    print("Example 4: Temperature Control")
    print("=" * 60)

    print("\nTemperature affects creativity vs consistency:")
    print("- Low (0.0-0.3): Deterministic, factual")
    print("- Medium (0.4-0.7): Balanced")
    print("- High (0.8-1.0): Creative, varied")
    print()

    try:
        # Build model with custom temperature
        model_creative = llm_loader.build_model("openrouter", temperature=0.9)
        model_factual = llm_loader.build_model("openrouter", temperature=0.1)

        print("✓ Models configured with different temperatures")
        print("  - Creative (0.9): Good for stories, brainstorming")
        print("  - Factual (0.1): Good for analysis, coding")
        print()

    except Exception as e:
        print(f"Note: {str(e)}")
        print()


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("OpenRouter Usage Examples for LLM-PKG")
    print("=" * 60)
    print()

    # Example 1: Simple query
    await example_simple_query()

    # Example 2: Document query
    await example_document_query()

    # Example 3: Model comparison
    example_model_comparison()

    # Example 4: Temperature control
    await example_with_temperature()

    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print()
    print("1. Add credits at: https://openrouter.ai/credits")
    print("2. Choose your preferred model in config/llm_config.toml")
    print("3. Run examples:")
    print()
    print("   # Test configuration")
    print("   python tools/openrouter_test.py")
    print()
    print("   # Run this example")
    print("   python examples/openrouter_example.py")
    print()
    print("   # Start server and use API")
    print("   llm-pkg-server")
    print()
    print("   # Use CLI")
    print("   llm-pkg")
    print()
    print("See OPENROUTER_USAGE.md for complete guide!")
    print()


if __name__ == "__main__":
    asyncio.run(main())

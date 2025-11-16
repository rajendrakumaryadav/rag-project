#!/usr/bin/env python3
"""
OpenRouter Testing Script
Test your OpenRouter configuration and compare different models
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm_pkg.config import llm_loader

console = Console()


def test_openrouter_config():
    """Test if OpenRouter is configured."""
    console.print("\n[bold cyan]🔍 Checking OpenRouter Configuration[/bold cyan]\n")

    openrouter_providers = [
        name for name in llm_loader.providers.keys() if "openrouter" in name.lower()
    ]

    if not openrouter_providers:
        console.print("[red]❌ No OpenRouter providers configured[/red]")
        console.print("\nTo configure OpenRouter:")
        console.print("1. Get API key from https://openrouter.ai/keys")
        console.print("2. Edit config/llm_config.toml")
        console.print("3. Add your key to [openrouter] section")
        return False

    table = Table(title="OpenRouter Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Status", style="yellow")

    for name in openrouter_providers:
        cfg = llm_loader.providers[name]
        status = (
            "⚠️ Not configured"
            if "<SET_OPENROUTER_KEY>" in str(cfg.meta)
            else "✅ Ready"
        )
        table.add_row(name, cfg.model, status)

    console.print(table)
    return True


def test_simple_query(provider_name: str):
    """Test a simple query with OpenRouter."""
    console.print(f"\n[bold cyan]🧪 Testing {provider_name}[/bold cyan]\n")

    try:
        model = llm_loader.build_model(provider_name)
        console.print(f"[green]✅ Model loaded: {type(model).__name__}[/green]")

        # Simple test
        question = "What is 2+2? Answer in one sentence."
        console.print(f"[yellow]Question: {question}[/yellow]")

        response = model.invoke(question)
        answer = response.content if hasattr(response, "content") else str(response)

        console.print(
            Panel(answer, title=f"Response from {provider_name}", border_style="green")
        )

        return True

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

        if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
            console.print(
                "\n[yellow]💡 Tip: Check your OpenRouter API key in config/llm_config.toml[/yellow]"
            )
        elif "credits" in str(e).lower():
            console.print(
                "\n[yellow]💡 Tip: Add credits at https://openrouter.ai/credits[/yellow]"
            )

        return False


async def test_document_qa(provider_name: str):
    """Test document Q&A with OpenRouter."""
    console.print(
        f"\n[bold cyan]📄 Testing Document Q&A with {provider_name}[/bold cyan]\n"
    )

    try:
        from llm_pkg import QAEngine, graph_manager, save_document

        # Create a sample document
        sample_text = """
        Artificial Intelligence and Machine Learning
        
        Artificial Intelligence (AI) is transforming industries worldwide.
        Machine Learning (ML) is a subset of AI that enables systems to learn from data.
        Deep Learning uses neural networks to process complex patterns.
        
        Key applications include:
        - Natural Language Processing
        - Computer Vision
        - Robotics
        - Autonomous Vehicles
        """

        # Save document
        path = save_document(sample_text.encode(), "ai_overview.txt")
        console.print(f"[green]✅ Sample document created: {path.name}[/green]")

        # Query
        qa_engine = QAEngine(llm_loader, graph_manager)
        result = await qa_engine.query(
            question="What are the key applications mentioned?",
            provider=provider_name,
        )

        console.print(Panel(result["answer"], title="Q&A Answer", border_style="green"))

        console.print(f"\n[dim]Sources: {len(result['sources'])} documents[/dim]")

        return True

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False


async def compare_models():
    """Compare responses from different OpenRouter models."""
    console.print("\n[bold cyan]🔄 Comparing OpenRouter Models[/bold cyan]\n")

    providers = [
        name for name in llm_loader.providers.keys() if "openrouter" in name.lower()
    ]

    if not providers:
        console.print("[red]No OpenRouter providers configured[/red]")
        return

    question = "Explain machine learning in one sentence."
    console.print(f"[yellow]Question: {question}[/yellow]\n")

    results = []

    for provider in providers[:3]:  # Test up to 3 providers
        try:
            model = llm_loader.build_model(provider)
            response = model.invoke(question)
            answer = response.content if hasattr(response, "content") else str(response)
            results.append((provider, answer, "✅"))
        except Exception as e:
            results.append((provider, str(e)[:100], "❌"))

    # Display results
    table = Table(title="Model Comparison")
    table.add_column("Provider", style="cyan")
    table.add_column("Response", style="green")
    table.add_column("Status", style="yellow")

    for provider, response, status in results:
        table.add_row(provider, response[:150] + "...", status)

    console.print(table)


async def main():
    """Main test function."""
    console.print(
        Panel(
            "[bold cyan]OpenRouter Testing Tool[/bold cyan]\n\n"
            "This script tests your OpenRouter configuration and functionality.",
            border_style="cyan",
        )
    )

    # Test 1: Check configuration
    if not test_openrouter_config():
        return

    # Get first OpenRouter provider
    openrouter_providers = [
        name for name in llm_loader.providers.keys() if "openrouter" in name.lower()
    ]

    if not openrouter_providers:
        return

    first_provider = openrouter_providers[0]

    # Test 2: Simple query
    console.print("\n" + "=" * 60)
    if not test_simple_query(first_provider):
        console.print(
            "\n[yellow]⚠️  Basic test failed. Skipping advanced tests.[/yellow]"
        )
        console.print("\n[bold]Setup Steps:[/bold]")
        console.print("1. Visit https://openrouter.ai/keys")
        console.print("2. Create an API key")
        console.print("3. Add credits (minimum $5)")
        console.print("4. Edit config/llm_config.toml")
        console.print("5. Replace <SET_OPENROUTER_KEY> with your actual key")
        console.print("6. Run this script again")
        return

    # Test 3: Document Q&A
    console.print("\n" + "=" * 60)
    await test_document_qa(first_provider)

    # Test 4: Compare models
    if len(openrouter_providers) > 1:
        console.print("\n" + "=" * 60)
        await compare_models()

    # Summary
    console.print("\n" + "=" * 60)
    console.print(
        Panel(
            "[bold green]✅ All tests completed![/bold green]\n\n"
            "Your OpenRouter configuration is working correctly.\n"
            "You can now use OpenRouter in your queries:\n\n"
            f"  • API: provider={first_provider}\n"
            f"  • CLI: llm-pkg query 'Your question' --provider {first_provider}\n"
            f"  • Python: llm_loader.build_model('{first_provider}')",
            title="Test Summary",
            border_style="green",
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        import traceback

        traceback.print_exc()

"""
CLI Tool for LLM-PKG
====================
Command-line interface for interacting with the LLM-PKG platform.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from llm_pkg.config import llm_loader
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from llm_pkg.storage import list_document_metadata, save_document

console = Console()
logger = logging.getLogger("llm_pkg.cli")


class CLI:
    """Command-line interface for LLM-PKG."""
    
    def __init__(self):
        from llm_pkg.config import graph_manager
        self.doc_processor = DocumentProcessor()
        self.qa_engine = QAEngine(llm_loader, graph_manager)
    
    async def upload_document(self, file_path: str):
        """Upload and process a document."""
        path = Path(file_path)
        
        if not path.exists():
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            return
        
        console.print(f"[cyan]Uploading document: {path.name}[/cyan]")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing...", total=100)
            
            # Read file
            with open(path, "rb") as f:
                content = f.read()
            progress.update(task, advance=30)
            
            # Save document
            saved_path = save_document(content, path.name)
            progress.update(task, advance=30)
            
            # Process document
            processed = await self.doc_processor.process_document(saved_path)
            progress.update(task, advance=40)
        
        # Display results
        console.print(Panel(
            f"[green]✓[/green] Document uploaded successfully!\n\n"
            f"[bold]Filename:[/bold] {processed['filename']}\n"
            f"[bold]Format:[/bold] {processed['format']}\n"
            f"[bold]Summary:[/bold] {processed['summary']}",
            title="Upload Complete",
            border_style="green",
        ))
    
    def list_documents(self):
        """List all uploaded documents."""
        docs = list_document_metadata()
        
        if not docs:
            console.print("[yellow]No documents uploaded yet.[/yellow]")
            return
        
        table = Table(title="Uploaded Documents")
        table.add_column("Filename", style="cyan")
        table.add_column("Size", justify="right", style="green")
        table.add_column("Uploaded At", style="yellow")
        
        for doc in docs:
            size_kb = doc.size_bytes / 1024
            table.add_row(
                doc.name,
                f"{size_kb:.2f} KB",
                doc.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        
        console.print(table)
    
    async def query(self, question: str, provider: str | None = None, document: str | None = None):
        """Execute a query."""
        console.print(f"\n[cyan]Question:[/cyan] {question}\n")
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Processing query...", total=100)
            
            result = await self.qa_engine.query(
                question=question,
                provider=provider,
                document_name=document,
            )
            progress.update(task, advance=100)
        
        # Display answer
        console.print(Panel(
            f"[bold green]Answer:[/bold green]\n\n{result['answer']}",
            title="Response",
            border_style="green",
        ))
        
        # Display sources
        if result.get("sources"):
            console.print("\n[bold]Sources:[/bold]")
            for i, source in enumerate(result["sources"], 1):
                console.print(
                    f"  {i}. {source['source']} "
                    f"(Page {source.get('page', 'N/A')})"
                )
    
    def show_config(self):
        """Display current configuration."""
        table = Table(title="LLM Configuration")
        table.add_column("Name", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Default", style="magenta")
        
        for name, cfg in llm_loader.providers.items():
            is_default = "✓" if llm_loader.default and llm_loader.default.provider == cfg.provider else ""
            table.add_row(name, cfg.provider, cfg.model, is_default)
        
        console.print(table)
    
    def interactive_mode(self):
        """Run in interactive mode."""
        console.print(Panel(
            "[bold cyan]LLM-PKG Interactive Mode[/bold cyan]\n\n"
            "Commands:\n"
            "  upload <file>     - Upload a document\n"
            "  list              - List documents\n"
            "  query <question>  - Ask a question\n"
            "  config            - Show configuration\n"
            "  exit              - Exit interactive mode",
            border_style="cyan",
        ))
        
        while True:
            try:
                command = console.input("\n[bold cyan]llm-pkg>[/bold cyan] ").strip()
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd == "exit":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif cmd == "upload":
                    if args:
                        asyncio.run(self.upload_document(args))
                    else:
                        console.print("[red]Usage: upload <file_path>[/red]")
                elif cmd == "list":
                    self.list_documents()
                elif cmd == "query":
                    if args:
                        asyncio.run(self.query(args))
                    else:
                        console.print("[red]Usage: query <question>[/red]")
                elif cmd == "config":
                    self.show_config()
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


def main():
    """Main entry point for CLI."""
    import sys
    
    cli = CLI()
    
    if len(sys.argv) == 1:
        # Interactive mode
        cli.interactive_mode()
    else:
        # Command mode
        command = sys.argv[1]
        
        if command == "upload" and len(sys.argv) > 2:
            asyncio.run(cli.upload_document(sys.argv[2]))
        elif command == "list":
            cli.list_documents()
        elif command == "query" and len(sys.argv) > 2:
            question = " ".join(sys.argv[2:])
            asyncio.run(cli.query(question))
        elif command == "config":
            cli.show_config()
        else:
            console.print("[red]Usage: llm-pkg [upload|list|query|config] [args][/red]")


if __name__ == "__main__":
    main()

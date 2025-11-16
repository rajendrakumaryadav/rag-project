#!/usr/bin/env python3
"""
Installation verification script for LLM-PKG
Checks if all components are properly set up
"""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(
            f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.11+)"
        )
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\n📦 Checking dependencies...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langgraph",
        "pdfplumber",
        "pypdf",
        "rich",
        "tomli",
    ]
    required_files = [
        # src-layout package files
        "src/llm_pkg/__init__.py",
        "src/llm_pkg/app.py",
        "src/llm_pkg/config.py",
        "src/llm_pkg/document_processor.py",
        "src/llm_pkg/qa_engine.py",
        "src/llm_pkg/storage.py",
        "src/llm_pkg/cli.py",
        # project-level files
        "config/llm_config.toml",
        "pyproject.toml",
        "README.md",
    ]

    required_dirs = [
        "data/uploads",
        "tests",
        "src",
    ]

    all_exist = True

    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
            all_exist = False

    for dir_path in required_dirs:
        if Path(dir_path).is_dir():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (missing)")
            all_exist = False

    return all_exist


def check_configuration():
    """Check configuration."""
    print("\n⚙️ Checking configuration...")

    config_file = Path("config/llm_config.toml")
    if config_file.exists():
        print("   ✅ Configuration file exists")

        # Check for placeholder API keys
        content = config_file.read_text()
        if "<SET_OPENAI_KEY>" in content or "<SET_AZURE_KEY>" in content:
            print("   ⚠️  API keys not configured (using placeholders)")
            print("      Edit config/llm_config.toml with your actual API keys")
            return False
        else:
            print("   ✅ Configuration appears to be customized")
            return True
    else:
        print("   ❌ Configuration file missing")
        return False


def check_imports():
    """Check if main package imports work."""
    print("\n🔧 Checking package imports...")

    try:
        from llm_pkg import __version__
        from llm_pkg.config import llm_loader
        from llm_pkg.document_processor import DocumentProcessor
        from llm_pkg.qa_engine import QAEngine

        print(f"   ✅ llm_pkg imported (version {__version__})")
        # Instantiate lightweight objects to ensure imports are wired
        _ = DocumentProcessor()
        print("   ✅ DocumentProcessor imported")
        _ = llm_loader
        print("   ✅ llm_loader imported")
        _ = QAEngine  # class reference is sufficient
        print("   ✅ QAEngine imported")

        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def print_summary(checks):
    """Print summary of checks."""
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)

    total = len(checks)
    passed = sum(checks.values())

    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check_name}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 All checks passed! Your installation is ready.")
        print("\nNext steps:")
        print("  1. Configure API keys in config/llm_config.toml")
        print("  2. Run the server: make run")
        print("  3. Or use the CLI: make cli")
        print("  4. Visit http://localhost:8000/docs for API documentation")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nTo fix:")
        print("  1. Run: uv pip install -e .")
        print("  2. Ensure all files are in place")
        print("  3. Configure config/llm_config.toml")


def main():
    """Run all verification checks."""
    print("LLM-PKG Installation Verification")
    print("=" * 50)

    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Project Structure": check_project_structure(),
        "Configuration": check_configuration(),
        "Package Imports": check_imports(),
    }

    print_summary(checks)

    return all(checks.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

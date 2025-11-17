#!/usr/bin/env python3
"""
Token count helper using tiktoken.
Usage: python tools/token_check.py --model gpt-4o --text "Some text here"
"""

import argparse

try:
    import tiktoken
except ImportError:
    print("Please install tiktoken in the virtualenv: pip install tiktoken")
    raise


def count_tokens(model: str, text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        print(f"Warning: no exact encoder for {model}, using cl100k_base fallback")
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def main():
    parser = argparse.ArgumentParser(
        description="Count tokens for a text given a model"
    )
    parser.add_argument(
        "--model", required=True, help="Model name (e.g., gpt-4o or openai/gpt-4o)"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Text to encode (wrap in quotes) or path: file://path.txt",
    )
    args = parser.parse_args()

    text = args.text
    if args.text.startswith("file://"):
        path = args.text[len("file://") :]
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    tokens = count_tokens(args.model, text)
    print(f"Model: {args.model}")
    print(f"Text length: {len(text)} chars")
    print(f"Token count: {tokens}")


if __name__ == "__main__":
    main()

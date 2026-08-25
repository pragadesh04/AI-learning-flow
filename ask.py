#!/usr/bin/env python3
"""
ask.py — Interactive CLI for the Insurance Claims RAG app.

Ask anything about the indexed endorsements and get a grounded, cited answer —
or an honest refusal when the corpus does not cover it. Type 'quit' to leave.

Usage:
    python ask.py
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()  # load GROQ_API_KEY from .env before importing anything that needs it

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from answerer import generate_answer
from retriever import search

# ── ANSI colours ────────────────────────────────────────────────────────────
CYAN, GREEN, YELLOW, RED = "\033[96m", "\033[92m", "\033[93m", "\033[91m"
BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"

QUIT_WORDS = {"quit", "exit", "q", "bye"}

BANNER = f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════╗
║       🏠  Insurance Claims RAG — Endorsement Assistant       ║
║              Week 3 Practical · Task Set D                   ║
╚══════════════════════════════════════════════════════════════╝{RESET}

{DIM}Indexed: HO-0304, HO-0305, HO-0306, HO-0307, HO-0308, HO-0309
Type your question below, or {BOLD}quit{RESET}{DIM} to exit.{RESET}

{YELLOW}Try one of these:{RESET}
  • Is mold remediation ever payable under HO-0306, and up to what limit?
  • What does CLAUSE EM-2 say about concurrent causes in HO-0308?
  • How current must an appraisal be for scheduled items under HO-0307?
  • What is the in-home office equipment sublimit under HO-0309?
"""


def ask(question: str) -> None:
    """One turn: retrieve, show what came back, then generate a grounded answer."""
    try:
        hits = search(question, strategy="structure_aware", n_results=5)
    except Exception as exc:
        print(f"{RED}Retrieval error: {exc}{RESET}")
        print(f"{DIM}Have you built the index yet? Run: python src/indexer.py{RESET}")
        return

    if not hits:
        print(f"{YELLOW}Nothing indexed matched that. Run: python src/indexer.py{RESET}")
        return

    print(f"\n{DIM}Found {len(hits)} chunks:{RESET}")
    for hit in hits[:3]:
        meta = hit["metadata"]
        print(
            f"   {DIM}#{hit['rank']} score={hit['score']:.3f} │ "
            f"{meta.get('form_number', '?')} │ {meta.get('clause_id', '?')}{RESET}"
        )

    print(f"{DIM}  thinking...{RESET}", end="\r")
    try:
        result = generate_answer(question, hits, verbose=False)
    except KeyboardInterrupt:
        print(f"{YELLOW}  cancelled.        {RESET}")
        return
    except Exception as exc:
        print(f"{RED}Generation error: {exc}{RESET}")
        return

    if result["is_refusal"]:
        print(f"\n{BOLD}{RED}Assistant (REFUSAL):{RESET}\n{result['answer']}")
        return

    top = hits[0]["metadata"]
    print(f"\n{BOLD}{GREEN}Assistant:{RESET}\n{result['answer']}")
    print(
        f"\n{DIM}Primary source: {top.get('source_file', '?')} │ "
        f"form={top.get('form_number', '?')} │ "
        f"clause={top.get('clause_id', '?')}{RESET}"
    )


def main() -> None:
    print(BANNER)

    if not os.environ.get("GROQ_API_KEY"):
        print(f"{RED}GROQ_API_KEY is not set.{RESET}")
        print("Copy .env.example to .env and put your Groq key in it, then try again.\n")
        sys.exit(1)

    while True:
        print(f"{DIM}{'─' * 64}{RESET}")
        try:
            question = input(f"\n{BOLD}{CYAN}You:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not question:
            print(f"{DIM}  (empty input — please type a question){RESET}")
            continue
        if question.lower() in QUIT_WORDS:
            break

        ask(question)

    print(f"\n{DIM}Goodbye!{RESET}\n")


if __name__ == "__main__":
    main()

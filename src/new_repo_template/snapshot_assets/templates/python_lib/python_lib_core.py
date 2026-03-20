from __future__ import annotations


def build_greeting(subject: str) -> str:
    normalized_subject = subject.strip() or "terminal builder"
    return (
        f"Hello, {normalized_subject}! This Python CLI is powered by python-lib "
        "inside the shared uv workspace."
    )

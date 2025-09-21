"""Adapter to call Google Generative AI (Gemini) when configured.

This module is optional. If the `google-generativeai` package or API
credentials are missing the functions will raise a controlled exception
and the caller should fall back to the local mock LLM.

Usage: set environment variable GOOGLE_API_KEY or provide
GOOGLE_APPLICATION_CREDENTIALS pointing to a service account JSON.
You can also set GEMINI_MODEL to the desired model (default: chat-bison).
"""
from typing import List, Dict, Any, Optional
import os
import logging

logger = logging.getLogger("genai_legal.gemini")

try:
    import google.generativeai as genai  # type: ignore
    _HAS_GENAI = True
except Exception:
    genai = None  # type: ignore
    _HAS_GENAI = False


def is_configured() -> bool:
    """Return True if the adapter appears configured and the library is present."""
    if not _HAS_GENAI:
        return False
    if os.environ.get("GOOGLE_API_KEY"):
        return True
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return True
    return False


def generate_answer_gemini(question: str, relevant_clauses: List[Dict[str, Any]]) -> Optional[str]:
    """Generate an answer using Google Generative AI.

    Returns the assistant text or None on failure.
    """
    if not is_configured():
        logger.debug("Gemini adapter not configured")
        return None

    try:
        # Configure the library with explicit API key if provided
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

        model = os.environ.get("GEMINI_MODEL", "chat-bison")
        # Compose a concise prompt with context
        context_parts = [f"Clause {i+1}: {c.get('original_text','')}" for i, c in enumerate(relevant_clauses[:6])]
        context = "\n".join(context_parts)

        system_prompt = (
            "You are an assistant that answers questions specifically about the provided legal document. "
            "Answer concisely and cite clause numbers when relevant. If the information is not in the provided clauses, say you couldn't find it."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Document context:\n{context}\n\nQuestion: {question}"},
        ]

        # Use the chat.create API if available; fall back to text generation
        if hasattr(genai, 'chat'):
            resp = genai.chat.create(model=model, messages=messages)
            # The library returns a structure with 'candidates' or 'output'
            if resp and getattr(resp, 'candidates', None):
                text = resp.candidates[0].content if resp.candidates[0].content else getattr(resp, 'output', '')
            else:
                text = getattr(resp, 'output', '') or str(resp)
        else:
            # Older generate_text interface
            prompt = system_prompt + "\n\n" + context + "\n\nQuestion: " + question
            resp = genai.generate_text(model=model, prompt=prompt)
            text = getattr(resp, 'text', str(resp))

        # Normalize and return
        if isinstance(text, (list, dict)):
            text = str(text)
        return text

    except Exception as e:
        logger.exception(f"Gemini generation failed: {e}")
        return None

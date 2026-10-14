"""Flashcard generator from raw text and fallback extraction."""
import re
from typing import List, Dict, Any
from .validation_service import validate_flashcards


def _clean_text(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return " ".join(lines)


def _sentences(text: str) -> List[str]:
    cleaned = _clean_text(text)
    # Split on sentence boundaries
    raw = re.split(r"(?<=[.!?])\s+", cleaned)
    return [s.strip() for s in raw if len(s.split()) >= 6 and len(s) >= 30]


def _legacy_generate_flashcards(text: str, count: int = 8) -> List[Dict[str, Any]]:
    """Heuristic fallback extraction for generating meaningful study cards when offline."""
    sents = _sentences(text)
    if not sents:
        return []

    raw_candidates = []
    seen_terms = set()

    # Pattern 1: Definitions ("X is defined as Y", "X refers to Y", "X is a Y that...")
    def_pattern = re.compile(
        r"^([A-Z][A-Za-z0-9\s\-]{2,35}?)\s+(?:is defined as|refers to|is an?|are|was|represents|describes)\s+(.+)",
        re.IGNORECASE
    )
    
    # Pattern 2: Function / Process ("X enables Y", "X provides Y", "X functions by Y")
    proc_pattern = re.compile(
        r"^([A-Z][A-Za-z0-9\s\-]{2,35}?)\s+(?:enables|allows|functions by|works by|provides|serves to|operates by)\s+(.+)",
        re.IGNORECASE
    )

    for i, s in enumerate(sents):
        s_clean = s.strip()
        m_def = def_pattern.match(s_clean)
        m_proc = proc_pattern.match(s_clean)
        
        if m_def:
            term = m_def.group(1).strip()
            rest = m_def.group(2).strip()
            if len(term.split()) <= 5 and term.lower() not in seen_terms and len(term) >= 3:
                seen_terms.add(term.lower())
                # Formulate a complete, meaningful answer
                answer = s_clean if s_clean.endswith(".") else s_clean + "."
                raw_candidates.append({
                    "id": len(raw_candidates) + 1,
                    "question": f"What is {term}?",
                    "answer": answer,
                    "type": "definition",
                    "topic": term,
                })
        elif m_proc:
            term = m_proc.group(1).strip()
            rest = m_proc.group(2).strip()
            if len(term.split()) <= 5 and term.lower() not in seen_terms and len(term) >= 3:
                seen_terms.add(term.lower())
                answer = s_clean if s_clean.endswith(".") else s_clean + "."
                raw_candidates.append({
                    "id": len(raw_candidates) + 1,
                    "question": f"How does {term} function?",
                    "answer": answer,
                    "type": "process",
                    "topic": term,
                })

    # If we need more candidates, extract key capitalized terms
    if len(raw_candidates) < count:
        for s in sents:
            if len(raw_candidates) >= count * 2:
                break
            # Find subject term
            words = s.split()
            first_caps = [w.strip(".,;:()") for w in words[:4] if w and w[0].isupper() and len(w) >= 4]
            if first_caps:
                term = first_caps[0]
                if term.lower() not in seen_terms and term.lower() not in {"this", "these", "there", "their", "however", "although", "furthermore", "moreover"}:
                    seen_terms.add(term.lower())
                    raw_candidates.append({
                        "id": len(raw_candidates) + 1,
                        "question": f"Explain the key concept of {term}.",
                        "answer": s.strip(),
                        "type": "concept",
                        "topic": term,
                    })

    return validate_flashcards({"flashcards": raw_candidates}, count=count)


def generate_flashcards(text: str, count: int = 8) -> List[Dict[str, Any]]:
    """Generate flashcards using RAG if available, or fallback."""
    try:
        from .generation_service import rag_generate_flashcards
        return rag_generate_flashcards(text, count=count)
    except Exception:
        return _legacy_generate_flashcards(text, count=count)

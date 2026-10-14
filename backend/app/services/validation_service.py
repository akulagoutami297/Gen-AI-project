import re
import string
from typing import List, Dict, Any, Optional

_STOPWORDS = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "be", "been", "this", "that", "it"}


def _normalize_text(text: str) -> str:
    """Normalize text by lowering, stripping punctuation, and extra whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return " ".join(text.split())


def _token_set(text: str) -> set:
    norm = _normalize_text(text)
    return set(norm.split()) - _STOPWORDS


def is_similar_question(q1: str, q2: str, threshold: float = 0.60) -> bool:
    """Determine whether two questions are identical or obvious near-duplicates."""
    n1 = _normalize_text(q1)
    n2 = _normalize_text(q2)
    if not n1 or not n2:
        return False
    if n1 == n2:
        return True
    if n1 in n2 or n2 in n1:
        return True
    
    tokens1 = _token_set(q1)
    tokens2 = _token_set(q2)
    if not tokens1 or not tokens2:
        return False
    
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union)
    return jaccard >= threshold


def validate_flashcards(data: Dict[str, Any], count: int = 8) -> List[Dict[str, Any]]:
    """Validate and filter flashcards ensuring clear questions and explanatory answers."""
    raw_cards = data.get("flashcards", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    
    out = []
    seen_questions = []

    for i, c in enumerate(raw_cards):
        if not isinstance(c, dict):
            continue
            
        q = (c.get("question") or "").strip()
        a = (c.get("answer") or "").strip()
        card_type = (c.get("type") or "concept").strip().lower()
        topic = (c.get("topic") or "").strip()
        
        # 1. Length checks
        if len(q) < 10 or len(a) < 15:
            continue
            
        # 2. Must look like a question
        if not q.endswith("?") and not any(q.lower().startswith(w) for w in ["what", "how", "why", "when", "where", "who", "which", "explain", "describe", "compare"]):
            q = q + "?"
            
        # 3. Reject bad patterns (e.g. meta questions or broken fragments)
        q_lower = q.lower()
        if any(bad in q_lower for bad in ["according to the text", "in the passage", "the author states", "as mentioned above"]):
            continue
        if q_lower in {"what is this?", "explain.", "what is data?"}:
            continue

        # 4. Answer must not simply be the question
        if _normalize_text(q) == _normalize_text(a):
            continue
            
        # 5. Duplicate check against existing cards in this batch
        if any(is_similar_question(q, seen_q, threshold=0.65) for seen_q in seen_questions):
            continue

        seen_questions.append(q)
        out.append({
            "id": i + 1,
            "question": q,
            "answer": a,
            "type": card_type if card_type in {"definition", "process", "comparison", "benefit", "concept"} else "concept",
            "topic": topic,
            "source_chunk_ids": c.get("source_chunk_ids", []),
        })
        
        if len(out) >= count:
            break

    return out


def validate_quiz(
    data: Dict[str, Any],
    exclude_questions: Optional[List[str]] = None,
    count: int = 5
) -> List[Dict[str, Any]]:
    """Validate and deduplicate quiz questions against current batch and previous questions."""
    raw_questions = data.get("questions", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    exclusions = exclude_questions or []
    
    out = []
    seen_in_batch = []

    for i, qd in enumerate(raw_questions):
        if not isinstance(qd, dict):
            continue
            
        q = (qd.get("question") or "").strip()
        opts = qd.get("options") or []
        explanation = (qd.get("explanation") or "").strip()
        difficulty = (qd.get("difficulty") or "medium").strip().lower()
        topic = (qd.get("topic") or "").strip()
        
        # 1. Question validity
        if len(q) < 12:
            continue
            
        # 2. Options validity (exactly 4 distinct non-empty strings)
        if not isinstance(opts, list) or len(opts) != 4:
            continue
        cleaned_opts = [str(o).strip() for o in opts if str(o).strip()]
        if len(set(cleaned_opts)) != 4:
            continue
            
        # 3. Correct answer validity
        correct = qd.get("correct") or qd.get("correct_answer") or qd.get("answer")
        if not correct or str(correct).strip() not in cleaned_opts:
            continue
        correct_str = str(correct).strip()

        # 4. Check for duplicates against previous questions (session exclusions)
        if any(is_similar_question(q, prev_q, threshold=0.58) for prev_q in exclusions):
            continue

        # 5. Check for duplicates within current batch
        if any(is_similar_question(q, seen_q, threshold=0.58) for seen_q in seen_in_batch):
            continue

        # 6. Fallback explanation if missing
        if not explanation:
            explanation = f"'{correct_str}' is the correct answer based on the provided document."

        seen_in_batch.append(q)
        out.append({
            "id": i + 1,
            "question": q,
            "options": cleaned_opts,
            "correct": correct_str,
            "correct_answer": correct_str,
            "explanation": explanation,
            "difficulty": difficulty if difficulty in {"easy", "medium", "hard"} else "medium",
            "topic": topic,
            "source_chunk_ids": qd.get("source_chunk_ids", []),
        })
        
        if len(out) >= count:
            break

    return out

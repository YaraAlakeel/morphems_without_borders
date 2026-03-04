"""
Morphological Productivity Evaluation Module.

This module provides utilities for evaluating language model performance
on Arabic morphological generation tasks.
"""

from .prompts import (
    build_prompt_with_optional_oneshot,
    PATTERN_SHOT,
    temperature,
)

from .utils import (
    extract_prediction,
    normalize_ar_for_compare,
    normalize_root,
    clean_ar_text,
    remove_arabic_diacritics_regex,
    remove_punct,
    extract_first_arabic_word,
    make_key,
    # Log-prob utilities
    extract_gen_sequence,
    compute_logprobs_from_scores,
    extract_avg_logprob_from_generate,
)

__all__ = [
    # Prompts
    "build_prompt_with_optional_oneshot",
    "PATTERN_SHOT",
    "temperature",
    # Text utilities
    "extract_prediction",
    "normalize_ar_for_compare",
    "normalize_root",
    "clean_ar_text",
    "remove_arabic_diacritics_regex",
    "remove_punct",
    "extract_first_arabic_word",
    "make_key",
    # Log-prob utilities
    "extract_gen_sequence",
    "compute_logprobs_from_scores",
    "extract_avg_logprob_from_generate",
]
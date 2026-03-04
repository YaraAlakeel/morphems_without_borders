import re
import unicodedata

# Optional torch import - only needed for logprob computation
try:
    import torch
    import torch.nn.functional as F
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

# === Arabic Regex Definitions ===
_AR_WORD_RE = re.compile(r"[\u0621-\u064A]+")
_AR_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]")
_ZERO_WIDTH = re.compile(r"[\u200B-\u200F\u202A-\u202E\u2066-\u2069]")
_TAG_RE = re.compile(r"<[^>]+>")
_AR_WORDS_RE = re.compile(r"[\u0600-\u06FF]+")
_AR_DIAC_RE = re.compile(r'[\u064B-\u0652\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7-\u06E8\u06EA-\u06ED]')



def remove_arabic_diacritics_regex (s: str) -> str:
    """
    Removes diacritics (tashkeel/harakat) from Arabic text using regular expressions.
    """
    # Unicode range for Arabic diacritics
    #arabic_diacritics_pattern = _AR_DIAC_RE
    return re.sub(u'[\u064e\u064f\u0650\u0651\u0652\u064c\u064b\u064d\u0640\ufc62]','',s)
    #return arabic_diacritics_pattern.sub('', s)

def remove_punct(s: str) -> str:
    """
    Remove (most) punctuation and symbols while keeping Arabic/Latin letters,
    digits and whitespace. This also removes Arabic punctuation: ، ؛ ؟ …
    """
    if not s:
        return ""
    # Keep Arabic block + word chars + whitespace; drop everything else to space
    return re.sub(r"[^\w\s\u0600-\u06FF]", " ", s)

def clean_ar_text(s: str) -> str:
    """Basic Arabic text cleanup: remove tags, diacritics, tatweel, and zero-width chars."""
    s = unicodedata.normalize("NFKC", s)
    s = _TAG_RE.sub(" ", s)
    s = _ZERO_WIDTH.sub("", s)
    s = s.replace("ـ", "")
    s = _AR_DIACRITICS.sub("", s)
    s= _AR_DIAC_RE.sub("",s)
    return s.strip()

def extract_first_arabic_word(text: str) -> str:
    """Extract the first Arabic word from text after cleaning."""
    if not text:
        return ""
    s = clean_ar_text(text)
    m = _AR_WORD_RE.search(s)
    return m.group(0) if m else ""

def normalize_ar_for_compare(s: str) -> str:
    """Normalize Arabic text for consistent comparison."""
    if not s:
        return ""
    return clean_ar_text(s)

def normalize_root(root: str) -> str:
    """Normalize Arabic root by removing dots and extra spaces."""
    return root.replace('.', '').replace(' ', '').strip()




def extract_gen_sequence(generate_out):
    """
    Returns a tuple (sequences_tensor, scores_list_or_None).
    Works whether generate() returned a tensor or a dict-like object.
    """
    if hasattr(generate_out, "sequences"):
        seq = generate_out.sequences
        scores = getattr(generate_out, "scores", None)
    else:
        # plain Tensor fallback
        seq = generate_out
        scores = None
    return seq, scores

def compute_logprobs_from_scores(scores, gen_ids):
    """
    Given `scores` (list of length T with logits per step) and the generated token ids,
    compute per-token logprobs and their average. Returns (list_of_logprobs, avg_logprob).
    
    Requires torch to be installed.
    """
    if not _TORCH_AVAILABLE:
        raise ImportError("torch is required for compute_logprobs_from_scores. Install with: pip install torch")
    if scores is None or len(gen_ids) == 0:
        return None, None

    token_logprobs = []
    # scores[t]: shape [batch, vocab]; gen_ids[t]: scalar token id at step t
    for t, logits in enumerate(scores):
        logp = F.log_softmax(logits, dim=-1)  # [B, V]
        tok_id = gen_ids[t]
        token_logprobs.append(logp[0, tok_id].item())
    avg_logprob = sum(token_logprobs) / len(token_logprobs) if token_logprobs else None
    return token_logprobs, avg_logprob

def extract_avg_logprob_from_generate(generate_out, input_len):
    """
    High-level: take the `generate()` output and the prompt length (input_len),
    and return (avg_logprob, per_token_logprobs) for the generated continuation.
    Returns (None, None) if scores are unavailable.
    
    Requires torch to be installed.
    """
    if not _TORCH_AVAILABLE:
        raise ImportError("torch is required for extract_avg_logprob_from_generate. Install with: pip install torch")
    seq, scores = extract_gen_sequence(generate_out)
    gen_ids = seq[0, input_len:]  # only continuation
    per_token, avg_lp = compute_logprobs_from_scores(scores, gen_ids)
    return avg_lp, per_token


def make_key(root, template_ex, pattern_ex):
    r = normalize_root(root) if 'normalize_root' in globals() else (root or "").strip()
    return (r, pattern_ex.strip())  # or (r, template_ex.strip(), pattern_ex.strip())


def extract_prediction(text: str, gold: str = None):
    """
    Extract the first Arabic word from Qwen output.

    Priority:
      1) Arabic word after '</think>' (case-insensitive)
      2) If no '</think>' and gold is found anywhere in the text, return gold
      3) Otherwise, first Arabic word anywhere in the text

    Returns:
      str or None
    """
    normalize_fn = globals()["normalize_ar_for_compare"]
    
    if not text:
        return None

    # --- 1) Arabic word after </think> ---
    parts = re.split(r"</think>", text, flags=re.IGNORECASE)
    if len(parts) >= 2:
        post_think = parts[1]
        m = re.search(r"[\u0600-\u06FF]+", post_think)
        if m:
            return m.group(0)

    # --- 2) No </think> → check if gold exists anywhere in text ---
    # if gold and gold in text:
    #     return gold
    # if gold:
    #     norm_gold = normalize_fn(gold)
    #     # Extract all Arabic tokens from the entire text
    #     arabic_tokens = _AR_WORDS_RE.findall(text)
    #     # Compare normalized tokens to normalized gold
    #     for tok in arabic_tokens:
    #         if normalize_fn(tok) == norm_gold:
    #             return gold  # return the gold form exactly, as requested
    # --- 2) No </think> → check if gold exists among Arabic tokens (punct removed) ---
    if gold:
        norm_gold = normalize_fn(gold)
        # Clean & de-punctuate the full text, then scan Arabic tokens
        text_no_punct = remove_punct(clean_ar_text(text))
        #print(text_no_punct)
        text_no_diacritics = remove_arabic_diacritics_regex(text_no_punct)
        #print(text_no_diacritics)
        arabic_tokens = _AR_WORDS_RE.findall(text_no_diacritics)
        for tok in arabic_tokens:
            if normalize_fn(tok) == norm_gold:
                return gold  # return the gold surface form exactly


    # --- 3) Fallback: first Arabic word anywhere ---
    m_any = re.search(r"[\u0600-\u06FF]+", text)
    if m_any:
        return m_any.group(0)

    return None

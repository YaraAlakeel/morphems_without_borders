import re

# ---------- Parsing ----------
def parse_line(line, line_num): #line_num is used to generate a unique sentence ID based on the line number.
    """
    Expects spans immediately (no sentence id, no tabs), e.g.:
      [(0,2), (2,4)] [(0,3), (3,5)] ...

    Returns: (sent_id: str, words: List[List[Tuple[int,int]]])
    """
    rest = line.strip()
    if not rest:
        return None, []

    line_id = f"LINE:{line_num}"
    words = []
    # each [...] block is one surface word
    word_chunks = re.findall(r"\[([^\]]*)\]", rest)
    for chunk in word_chunks:
        spans = re.findall(r"\((\d+),\s*(\d+)\)", chunk)
        words.append([(int(s), int(e)) for s, e in spans])
    return line_id, words


def load_file_to_dict(path):
    d = {}
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_id, words = parse_line(line, line_no)
            if line_id is not None:
                d[line_id] = words
    return d

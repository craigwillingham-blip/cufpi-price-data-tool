import re
from typing import List, Dict

PRICE_RE = re.compile(r"\$?([0-9]+\.[0-9]{2})")
SIZE_RE = re.compile(r"(\d+\s?(oz|lb|ct|gal|qt|pt|g|kg|ml|l))", re.IGNORECASE)


def parse_circular_text(text: str) -> List[Dict]:
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = PRICE_RE.search(line)
        if not m:
            continue
        price = float(m.group(1))
        size_match = SIZE_RE.search(line)
        size = size_match.group(1) if size_match else None
        name = PRICE_RE.sub("", line)
        if size:
            name = name.replace(size, "")
        name = name.strip(" -")
        items.append({"raw_text": line, "name": name, "size": size, "price": price})
    return items

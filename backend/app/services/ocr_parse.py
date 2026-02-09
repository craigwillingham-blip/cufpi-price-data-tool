import re
from typing import List, Dict

PRICE_RE = re.compile(r"\$?([0-9]+\.[0-9]{2})")


def parse_ocr_text(text: str) -> List[Dict]:
    items = []
    for line in text.splitlines():
        if len(line.strip()) < 3:
            continue
        m = PRICE_RE.search(line)
        if not m:
            continue
        price = float(m.group(1))
        name = PRICE_RE.sub("", line).strip()
        if not name:
            continue
        items.append({"raw_text": line, "name": name, "price": price})
    return items

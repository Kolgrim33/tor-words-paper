"""List every number typed literally in the paper's prose, so each can be checked by hand.

Results numbers are read from /results by Typst (paper/data.typ) and never appear as literals;
anything printed here should be a fixed fact (a year, a dataset size, a method setting).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "paper"
NUM = re.compile(r"(?<![\w.#/@-])\d[\d,.]*%?")

found = 0
for path in sorted(ROOT.rglob("*.typ")):
    if path.name == "data.typ":
        continue
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if line.lstrip().startswith(("//", "#set", "#show", "#import", "#let")):
            continue
        for m in NUM.finditer(line):
            found += 1
            print(f"{path.relative_to(ROOT)}:{i}: {m.group(0)}")
print(f"{found} literal numbers to review", file=sys.stderr)

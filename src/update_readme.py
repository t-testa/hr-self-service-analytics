"""Copies docs/reference_headlines.md (written by reference_kpis.py) into the README.

Run after reference_kpis.py:  python src/update_readme.py
Only the text between the KPI_START and KPI_END markers is replaced, so the numbers in the
README always come from a script run and never from typing.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    body = (ROOT / "docs" / "reference_headlines.md").read_text(encoding="utf-8").strip()
    body = body.replace("### ", "#### ")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- KPI_START -->\n).*?(<!-- KPI_END -->)", re.S)
    if not pattern.search(text):
        raise SystemExit("KPI markers not found in README.md")
    readme.write_text(pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text), encoding="utf-8", newline="\n")
    print("README KPI block updated")


if __name__ == "__main__":
    main()

"""Renders agent/test_prompts.csv into the tables of docs/03_evaluation.md and docs/04_results.md.

Run after editing the CSV:  python src/render_eval_table.py
Only the text between the START and END markers is replaced.
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def esc(text):
    return str(text).replace("|", "/")


def replace_block(path, name, body):
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- %s_START -->\n).*?(<!-- %s_END -->)" % (name, name), re.S)
    if not pattern.search(text):
        raise SystemExit("markers %s not found in %s" % (name, path))
    path.write_text(pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text), encoding="utf-8")


def main():
    df = pd.read_csv(ROOT / "agent" / "test_prompts.csv", encoding="utf-8")
    eval_rows = ["| ID | Category | Lang | Prompt | Expected behaviour | Expected value |", "|---|---|---|---|---|---|"]
    result_rows = ["| ID | Category | Result (Pass or Fail) | Value or behaviour observed | Flow triggered (Yes or No) | Notes |",
                   "|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        eval_rows.append("| %s | %s | %s | %s | %s | %s |" % (
            r.id, r.category, r.language, esc(r.prompt), esc(r.expected_behaviour), esc(r.expected_value)))
        result_rows.append("| %s | %s |  |  |  |  |" % (r.id, r.category))
    replace_block(ROOT / "docs" / "03_evaluation.md", "PROMPTS", "\n".join(eval_rows))
    replace_block(ROOT / "docs" / "04_results.md", "RESULTS", "\n".join(result_rows))
    print("Rendered %d prompts" % len(df))


if __name__ == "__main__":
    main()

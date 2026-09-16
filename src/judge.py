"""
judge.py — Week 6: the LLM judge, and the guard that keeps it blind.

The judge grades ONE binary criterion (COVERAGE_SUPPORTED). Its prompt lives
in evals/judge_vN.txt, a plain file, so v1 -> v2 is a readable diff.

The guard: the judge refuses to run until evals/labels_25.json holds 25 hand
labels, is committed to git, and has no uncommitted edits. The labels' commit
hash and commit time are written into every judge run, so "the labels came
first" is a fact the run file carries, not something the write-up asserts.
"""

import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from answerer import MODEL
from tracing import call_model

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
EVAL_DIR = os.path.join(ROOT, "evals")
ENDORSEMENTS_DIR = os.path.join(ROOT, "endorsements")
LABELS_PATH = os.path.join(EVAL_DIR, "labels_25.json")

JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 2000        # gpt-oss reasons before it answers

_VERDICT_RE = re.compile(r"VERDICT:\s*\**\s*(PASS|FAIL)", re.IGNORECASE)
_REASON_RE = re.compile(r"REASON:\s*(.+)", re.IGNORECASE)


class BlindProtocolError(RuntimeError):
    """The judge was asked to run before the human labels were provably fixed."""


def judge_path(version: str) -> str:
    return os.path.join(EVAL_DIR, f"judge_{version}.txt")


def load_template(version: str) -> str:
    with open(judge_path(version), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    # leading '#' lines are notes for humans, not part of the prompt
    while lines and lines[0].startswith("#"):
        lines.pop(0)
    return "\n".join(lines).strip() + "\n"


def criterion_text(version: str = "v1") -> str:
    """The CRITERION block, exactly as the judge sees it — shown to the labeller."""
    text = load_template(version)
    m = re.search(r"=== CRITERION ===\n(.*?)\n=== END CRITERION ===", text, re.DOTALL)
    return m.group(1).strip()


def policy_wording(forms: list[str]) -> str:
    """Full text of every endorsement on the policy — the same pages a human reads."""
    blocks = []
    for name in sorted(os.listdir(ENDORSEMENTS_DIR)):
        if name.split("_")[0] in forms:
            with open(os.path.join(ENDORSEMENTS_DIR, name), encoding="utf-8") as fh:
                blocks.append(fh.read().strip())
    return "\n\n".join(blocks)


def render(version: str, input_text: str, forms: list[str], output: str) -> str:
    return (load_template(version)
            .replace("{input}", input_text)
            .replace("{policy_wording}", policy_wording(forms))
            .replace("{output}", output))


def template_sha(version: str) -> str:
    return hashlib.sha256(load_template(version).encode("utf-8")).hexdigest()[:16]


def judge_one(version: str, input_text: str, forms: list[str], output: str) -> dict:
    prompt = render(version, input_text, forms, output)
    response, latency_ms = call_model(
        [{"role": "user", "content": prompt}],
        model=MODEL, temperature=JUDGE_TEMPERATURE, max_tokens=JUDGE_MAX_TOKENS,
    )
    raw = (response.choices[0].message.content or "").strip()
    verdicts = _VERDICT_RE.findall(raw)
    reason = _REASON_RE.search(raw)
    return {
        "verdict": verdicts[-1].upper() if verdicts else "UNPARSED",
        "reason": reason.group(1).strip() if reason else "",
        "raw": raw,
        "latency_ms": latency_ms,
        "finish_reason": response.choices[0].finish_reason,
    }


# ---------------------------------------------------------------------------
# The blind-protocol guard
# ---------------------------------------------------------------------------

def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=False).stdout.strip()


def labels_commit() -> dict:
    """
    Where labels_25.json entered git. Raises unless the labels are complete,
    committed, and unchanged since that commit.
    """
    import json

    if not os.path.exists(LABELS_PATH):
        raise BlindProtocolError("evals/labels_25.json does not exist — label first "
                                 "(python week6_eval.py label)")
    with open(LABELS_PATH, encoding="utf-8") as fh:
        labels = json.load(fh)["labels"]
    done = [l for l in labels.values() if l.get("label") in ("PASS", "FAIL")]
    if len(done) < 25:
        raise BlindProtocolError(f"only {len(done)}/25 labels recorded — finish labelling first")

    rel = os.path.relpath(LABELS_PATH, ROOT).replace("\\", "/")
    if _git("status", "--porcelain", "--", rel):
        raise BlindProtocolError(f"{rel} is not committed as it stands — commit the finished "
                                 f"labels BEFORE the judge runs; the commit is the ordering evidence")
    last = _git("log", "-1", "--format=%H %cI", "--", rel)
    if not last:
        raise BlindProtocolError(f"{rel} is not in git — commit it before the judge runs")
    # the worktree is clean, so the commit that last touched the file holds all 25 labels
    commit, commit_time = last.split(" ", 1)
    return {"commit": commit, "commit_time": commit_time}

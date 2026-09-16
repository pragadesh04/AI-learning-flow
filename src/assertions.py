"""
assertions.py — Week 6: the criteria that were taken OUT of the judge.

Each of these used to be a line in the judge rubric (evals/judge_v0.txt). None
of them needs a model: a claim number either is or is not CLM-YYYY-NNNNN, a
deductible either is or is not a number. A regex does it for free, the same
way every time, and a failure message says exactly what was wrong.

Every assertion returns (applies, passed, detail). A criterion that does not
apply to a case (no deductible on a liability-only claim, no claim record on a
replayed Q&A trace) is reported as n/a and never counted as a pass.
"""

import os
import re
import sys
from datetime import date, datetime
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from indexer import get_collection

HEADINGS = [
    "CLAIM NUMBER", "DATE OF LOSS", "POLICY FORMS", "LOSS SUMMARY",
    "DEDUCTIBLE", "COVERAGE POSITION", "EXCLUSIONS APPLIED", "OPEN ITEMS",
]

_HEADING_RE = re.compile(
    r"^[\s>*#_|-]*(" + "|".join(HEADINGS) + r")[\s*_]*:[\s*_]*",
    re.IGNORECASE | re.MULTILINE,
)


def sections(text: str) -> dict[str, str]:
    """Split a summary on its headed lines. Markdown bold/headers are tolerated."""
    found = list(_HEADING_RE.finditer(text or ""))
    out = {}
    for i, m in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        out.setdefault(m.group(1).upper(), text[m.end():end].strip())
    return out


# ---------------------------------------------------------------------------
# A1 — claim number echoed in CLM-YYYY-NNNNN form
# ---------------------------------------------------------------------------

_CLAIM_RE = re.compile(r"\bCLM-\d{4}-\d{5}\b")   # ASCII hyphens only, on purpose


def a1_claim_number(case: dict, output: str):
    expected = case.get("claim_number")
    if not expected:
        return False, None, "no claim record on this case"
    found = _CLAIM_RE.findall(output)
    if expected in found:
        return True, True, expected
    loose = re.findall(r"CLM\W?\d{4}\W?\d{5}", output)
    return True, False, (f"expected {expected}; canonical form absent"
                         + (f", saw {loose[0]!r}" if loose else ""))


# ---------------------------------------------------------------------------
# A2 — date of loss present and parseable
# ---------------------------------------------------------------------------

_DATE_FORMATS = [
    "%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d %Y", "%b %d %Y",
    "%m/%d/%Y", "%d/%m/%Y", "%m/%d/%y", "%d/%m/%y", "%d-%m-%Y",
]
_DATE_CANDIDATE = re.compile(
    r"\d{4}-\d{2}-\d{2}"
    r"|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r"|\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\.?,?\s+\d{4}"
    r"|[A-Za-z]{3,9}\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}"
)


def parse_dates(value: str) -> set[date]:
    """Every date a value could mean. Numeric day/month order is ambiguous, so both are tried."""
    out = set()
    for raw in _DATE_CANDIDATE.findall(value or ""):
        cleaned = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", raw)
        cleaned = cleaned.replace(",", " ").replace(".", " ")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        for fmt in _DATE_FORMATS:
            try:
                out.add(datetime.strptime(cleaned, fmt).date())
            except ValueError:
                pass
    return out


def a2_date_of_loss(case: dict, output: str):
    expected = case.get("date_of_loss")
    if not expected:
        return False, None, "no claim record on this case"
    value = sections(output).get("DATE OF LOSS")
    if value is None:
        return True, False, "no DATE OF LOSS line"
    parsed = parse_dates(value.splitlines()[0] if value else "")
    if not parsed:
        return True, False, f"DATE OF LOSS not parseable: {value[:40]!r}"
    want = date.fromisoformat(expected)
    if want in parsed:
        return True, True, expected
    return True, False, f"parsed {sorted(parsed)[0]}, expected {expected}"


# ---------------------------------------------------------------------------
# A3 — deductible / excess amount numeric
# ---------------------------------------------------------------------------

_MONEY_RE = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?")


def a3_deductible_numeric(case: dict, output: str):
    expected = case.get("deductible")
    if not expected:
        return False, None, "no property deductible on this case"
    value = sections(output).get("DEDUCTIBLE")
    if value is None:
        return True, False, "no DEDUCTIBLE line"
    amounts = {int(m.replace(",", "")) for m in _MONEY_RE.findall(value)}
    if not amounts:
        return True, False, f"no dollar amount: {value[:60]!r}"
    missing = [a for a in expected if a not in amounts]
    if missing:
        return True, False, f"expected ${', $'.join(f'{a:,}' for a in missing)}; saw {sorted(amounts)}"
    return True, True, ", ".join(f"${a:,}" for a in expected)


# ---------------------------------------------------------------------------
# A4 — an exclusion code is cited whenever a denial is stated
# ---------------------------------------------------------------------------

_NEGATED = re.compile(r"\b(?:not|never|is not|isn't|no longer)\s+(?:be\s+)?(?:excluded|denied)\b",
                      re.IGNORECASE)
_DENIAL = re.compile(
    r"\b(?:denied|deny|denial|declined?|excluded|not covered|not payable|no coverage)\b",
    re.IGNORECASE,
)
# U+2011 is accepted here: a reader still sees the code. A4 asks "is a code
# there", not "is it typed in ASCII" — that belongs to A5's citation parse.
_E_CODE = re.compile(r"\bE[-‑‐]\d{2}\b")


def a4_denial_cites_exclusion(case: dict, output: str):
    parts = sections(output)
    scope = " ".join(parts[h] for h in ("COVERAGE POSITION", "EXCLUSIONS APPLIED") if h in parts)
    scope = scope or output
    denial = _DENIAL.search(_NEGATED.sub(" ", scope))
    if not denial:
        return True, True, "no denial stated"
    codes = sorted(set(_E_CODE.findall(output)))
    if codes:
        return True, True, f"denial ({denial.group(0)!r}) cites {', '.join(codes)}"
    return True, False, f"states a denial ({denial.group(0)!r}) with no E-code anywhere"


# ---------------------------------------------------------------------------
# A5 — every source tag parses and resolves to the chunk it names
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(
    r"\[\s*SOURCE:\s*([^|\]]+?)\s*\|\s*([^|\]]+?)\s*\|\s*([^|\]]+?)\s*\]"
)


@lru_cache(maxsize=1)
def _chunk_index() -> dict[str, dict]:
    data = get_collection("structure_aware").get(include=["metadatas"])
    return dict(zip(data["ids"], data["metadatas"]))


def a5_citations_resolve(case: dict, output: str):
    mentions = len(re.findall(r"SOURCE\s*:", output))
    tags = _TAG_RE.findall(output)
    if mentions == 0:
        if output.startswith("REFUSAL:"):
            return False, None, "refusal carries no citations"
        return True, False, "no source tags at all"
    if len(tags) != mentions:
        return True, False, f"{mentions - len(tags)} of {mentions} source tags do not parse as [SOURCE: id | form | clause]"
    index = _chunk_index()
    for chunk_id, form, clause in tags:
        meta = index.get(chunk_id)
        if meta is None:
            return True, False, f"{chunk_id} does not resolve"
        if form != meta.get("form_number"):
            return True, False, f"{chunk_id} is {meta.get('form_number')}, tag says {form!r}"
        if clause != meta.get("clause_id"):
            return True, False, f"{chunk_id} clause is {meta.get('clause_id')}, tag says {clause!r}"
    return True, True, f"{len(tags)} tags resolve"


ASSERTIONS = {
    "A1_claim_number_CLM-YYYY-NNNNN": a1_claim_number,
    "A2_date_of_loss_parseable": a2_date_of_loss,
    "A3_deductible_numeric": a3_deductible_numeric,
    "A4_denial_cites_E-code": a4_denial_cites_exclusion,
    "A5_source_tags_resolve": a5_citations_resolve,
}


def run_assertions(case: dict, output: str) -> dict[str, dict]:
    results = {}
    for name, fn in ASSERTIONS.items():
        applies, passed, detail = fn(case, output)
        results[name] = {"applies": applies, "passed": passed if applies else None, "detail": detail}
    return results

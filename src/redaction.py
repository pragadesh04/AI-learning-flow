import re

__all__ = ["redact", "detect", "assert_clean", "RedactionError", "PLACEHOLDERS"]


class RedactionError(RuntimeError):
    """Raised when identifying text survives redaction on the write path."""


PLACEHOLDERS = {
    "claim_number": "[CLAIM_NUMBER]",
    "policy_number": "[POLICY_NUMBER]",
    "person_name": "[CLAIMANT_NAME]",
    "phone": "[PHONE]",
    "email": "[EMAIL]",
    "street_address": "[ADDRESS]",
}

# First names used by the claims roster. A gazetteer catches the bare
# "Denise Whitaker called" case that no keyword or title would reach.
_FIRST_NAMES = (
    "Aaron Alicia Amanda Andre Angela Anthony Arturo Beatriz Brenda Brian Carla "
    "Carlos Cheryl Christine Damon Daniel Danielle Darren Denise Diane Dominic "
    "Douglas Elena Elliot Emily Eric Esther Fatima Felix Fiona Frank Gabriel "
    "Gloria Gordon Grace Hannah Harold Hector Helen Ian Imani Irene Isaac Jacob "
    "Janet Jasmine Javier Jerome Joanna Jonathan Josephine Karen Keith Kelvin "
    "Laura Leonard Lorena Lucas Lydia Marcus Margaret Maria Marisol Martin "
    "Melanie Miguel Miriam Nadia Nathan Neil Nicole Olivia Omar Patricia Paul "
    "Priya Rachel Ramon Raymond Rebecca Renee Ricardo Robert Rosa Samuel Sandra "
    "Sean Selena Simone Sofia Stanley Stephanie Sylvia Terrence Theresa Thomas "
    "Tobias Valerie Vanessa Vincent Wanda Warren Yolanda Yusuf Zachary"
).split()

# [A-Z][A-Za-z]+ (not [A-Z][a-z]+) so "McAllister" and "DeSoto" are consumed
# whole; clipping a surname mid-token leaves a readable fragment in the log.
_NAME_TOKEN = r"[A-Z][A-Za-z]+(?:['’-][A-Za-z]+)?"
_NAME_TAIL = r"(?:\s+" + _NAME_TOKEN + r"){0,2}"

# Order matters: claim/policy numbers are consumed before the loose digit rules.
_DETECTORS: list[tuple[str, re.Pattern]] = [
    (
        "claim_number",
        re.compile(
            r"\b(?:CLM|CLA|CLB)[-\s]?\d{2,4}[-\s]?\d{3,8}\b"
            r"|\bclaim\s*(?:no\.?|number|num|#)\s*[:#]?\s*[A-Z]{0,4}[-\s]?\d[\d-]{2,}\b",
            re.IGNORECASE,
        ),
    ),
    (
        "policy_number",
        re.compile(
            r"\bHOP[-\s]?\d{5,10}\b"
            r"|\bpolicy\s*(?:no\.?|number|num|#)\s*[:#]?\s*[A-Z]{0,4}[-\s]?\d[\d-]{3,}\b",
            re.IGNORECASE,
        ),
    ),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b")),
    ("phone", re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")),
    (
        "street_address",
        re.compile(
            r"\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?\s+"
            r"(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct|Way|Boulevard|Blvd)\b\.?",
        ),
    ),
    (
        "person_name",
        re.compile(
            # 1) a title: Mr. Alvarez, Ms Denise Whitaker
            r"\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+" + _NAME_TOKEN + _NAME_TAIL
            # 2) a claims keyword introducing a capitalised name
            + r"|\b(?:claimant|insured|policyholder|homeowner|named insured|"
            r"contact|adjuster|handler|caller)\s+(?:is\s+|named\s+)?"
            + _NAME_TOKEN + _NAME_TAIL
            # 3) a roster first name, with or without a surname
            + r"|\b(?:" + "|".join(_FIRST_NAMES) + r")\b" + _NAME_TAIL
        ),
    ),
]


def detect(text: str) -> dict[str, list[str]]:
    """Every identifier the detectors can see in *text*, keyed by kind."""
    found: dict[str, list[str]] = {}
    for kind, pattern in _DETECTORS:
        matches = [m.group(0) for m in pattern.finditer(text or "")]
        if matches:
            found[kind] = matches
    return found


def redact(text: str, keep: tuple[str, ...] = ()) -> tuple[str, dict[str, int]]:
    """
    Replace every detected identifier with its placeholder.

    Returns the redacted text and a count per kind — the counts go into the
    trace so a reader can see redaction ran without seeing what it removed.

    `keep` names kinds to leave in place. Week 6: a claim summary has to echo
    the claim number, so the summariser keeps that one kind and nothing else.
    """
    if not text:
        return text, {}
    counts: dict[str, int] = {}
    out = text
    for kind, pattern in _DETECTORS:
        if kind in keep:
            continue
        out, n = pattern.subn(PLACEHOLDERS[kind], out)
        if n:
            counts[kind] = counts.get(kind, 0) + n
    return out, counts


def assert_clean(payload: str, where: str = "trace record") -> None:
    """Raise rather than write. This is the guard that makes the log safe."""
    leaks = detect(payload)
    if leaks:
        kinds = ", ".join(f"{k}x{len(v)}" for k, v in leaks.items())
        raise RedactionError(
            f"refusing to write {where}: identifiers survived redaction ({kinds})"
        )


if __name__ == "__main__":
    sample = (
        "Claimant Denise Whitaker, claim no. CLM-2024-04417 on policy HOP-4471932, "
        "reached at 555-021-4417 or d.whitaker@example.com, reports a burst supply "
        "line at 118 Marlow Street under HO-0304 ed. 03-24."
    )
    cleaned, counts = redact(sample)
    print("BEFORE:", sample, "\nAFTER :", cleaned, "\nCOUNTS:", counts)
    assert_clean(cleaned)
    print("guard passed — form number HO-0304 ed. 03-24 survived, identifiers did not")

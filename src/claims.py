"""
claims.py — Week 7: the ten claims the agent and the workflow both triage.

The corpus is a small adjuster system that the endorsement index does NOT
cover. Two tools straddle it:

    get_claim      reads this file  (claim record + adjuster notes)
    search_policy  reads the indexed endorsements  (the wording)

That split is the whole point of the week: the claim side is the *input*, the
policy side is the *authority*, and the only way to triage a claim honestly is
to consult both. The exclusion codes a claim turns on are never in the notes.

Ground truth (`EXPECTED`) was written from endorsements/ by reading the
exclusion tables and clauses, BEFORE anything was run. It is not derived from
the agent, the workflow, or any retrieval output — otherwise the pass rate
would be measuring this file rather than either system.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CLAIMS_DIR = os.path.join(HERE, "..", "claims")

FORMS = ["HO-0304", "HO-0305", "HO-0306", "HO-0307", "HO-0308", "HO-0309"]

# Every exclusion code that exists in the corpus, per form. Used to tell a real
# clause reference from fluent fiction (Week 8 argument validity).
REAL_CODES = {
    "HO-0304": [f"E-{n}" for n in range(10, 19)],
    "HO-0305": [f"E-{n}" for n in range(20, 25)],
    "HO-0306": [f"E-{n}" for n in range(22, 28)],
    "HO-0307": [f"E-{n}" for n in range(28, 33)],
    "HO-0308": [f"E-{n}" for n in range(31, 36)],
    "HO-0309": [f"E-{n}" for n in range(19, 20)] + [f"E-{n}" for n in range(36, 40)],
}

# Statuses the triage decision may take. Mirrored verbatim as the enum on
# compute_payout's claim_status parameter, and used by the outcome grader.
STATUSES = ["PAY", "DENY", "REFER"]


# ---------------------------------------------------------------------------
# The ten claims
# ---------------------------------------------------------------------------

CLAIMS = [
    {
        "case_id": "c01",
        "claim_number": "CLM-2024-31842",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 300000,
        "date_of_loss": "2024-06-11",
        "amount_claimed_usd": 6200,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "Claim CLM-2024-31842. Insured Denise Whitaker, HO-0304 ed. 03-24 on the "
            "dwelling, AOP excess $1,000. Loss date 11 June 2024. Inspected 13 June: the "
            "supply line to the upstairs toilet burst overnight and flooded the bathroom "
            "ceiling and the basement carpet. No gradual damp on inspection, the pipe was "
            "cut open and the break face is clean. Sump pump working, no water at the doors "
            "or windows. Contractor estimate to repair and dry: $6,200."
        ),
    },
    {
        "case_id": "c02",
        "claim_number": "CLM-2024-40271",
        "policy_forms": ["HO-0304", "HO-0306"],
        "coverage_a_limit_usd": 415000,
        "date_of_loss": "2024-07-08",
        "amount_claimed_usd": 8250,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-40271 / insured Marcus Bell / forms HO-0304 03-24 + HO-0306 04-24, "
            "AOP excess $1,000. Supply line to upstairs toilet burst 7/8/24, reported the "
            "next morning so inside the reporting window. Mold found behind drywall two "
            "weeks later. Licensed remediation contractor estimate on file, $7,400. Insured "
            "also submitted an $850 invoice from an air quality testing lab and wants both "
            "paid."
        ),
    },
    {
        "case_id": "c03",
        "claim_number": "CLM-2024-51908",
        "policy_forms": ["HO-0305"],
        "coverage_a_limit_usd": 300000,
        "date_of_loss": "2024-08-22",
        "amount_claimed_usd": 4150,
        "excess_usd": 0,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-51908, insured Priya Raman, HO-0305 ed. 03-24 named storm endorsement, "
            "Coverage A limit $300,000. Hurricane Ida 22 August 2024. Roof inspection found two "
            "lifted shingles and a broken gutter, tarps fitted the same day. Roofer's repair "
            "invoice totals $4,150 including materials. Insured believes a hurricane is always "
            "paid in full."
        ),
    },
    {
        "case_id": "c04",
        "claim_number": "CLM-2024-60337",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 340000,
        "date_of_loss": "2024-09-14",
        "amount_claimed_usd": 21000,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-60337, insured Hector Ramos, HO-0304 ed. 03-24, excess $1,000. Storm "
            "14 September 2024, six inches of rain in one day. Water came in through the open "
            "garage door and under the exterior door sweep; the whole slab and the bottom two "
            "feet of drywall are wet. Restoration contractor invoice $21,000. No burst pipe "
            "and no appliance overflow found."
        ),
    },
    {
        "case_id": "c05",
        "claim_number": "CLM-2024-71460",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 275000,
        "date_of_loss": "2024-10-02",
        "amount_claimed_usd": 9300,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-71460, insured Rosa Delgado, HO-0304 ed. 03-24, excess $1,000. 2 October "
            "2024, a municipal main on the street backed up overnight and sewage came up through "
            "the lowest bathroom floor drain and the basement laundry drain. No rain that week "
            "and no supply line break. Plumber invoice to clean and replace flooring $9,300."
        ),
    },
    {
        "case_id": "c06",
        "claim_number": "CLM-2024-82115",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 310000,
        "date_of_loss": "2024-11-19",
        "amount_claimed_usd": 16800,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-82115, insured Ahmed Yusuf, HO-0304 ed. 03-24, excess $1,000. Inspected "
            "19 November 2024: damp carpet along the north basement wall and a crescent of "
            "efflorescence on the slab, six inches deep. Water is standing in the soil against "
            "the foundation. No entry at any door or window, dry everywhere above the slab, and "
            "the sump pump runs but cannot keep up. Remediation and slab repair $16,800."
        ),
    },
    {
        "case_id": "c07",
        "claim_number": "CLM-2024-90224",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 265000,
        "date_of_loss": "2024-04-30",
        "amount_claimed_usd": 3200,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-90224, insured Gloria Mensah, HO-0304 ed. 03-24, excess $1,000. Slow drip "
            "from the outdoor hose bib noticed in the last week of April. Drywall and trim water "
            "stained over the following six weeks; the stain grew steadily rather than all at "
            "once. Painter and drywall invoice $3,200. Insured says it 'suddenly appeared'."
        ),
    },
    {
        "case_id": "c08",
        "claim_number": "CLM-2023-77651",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 245000,
        "date_of_loss": "2023-12-17",
        "amount_claimed_usd": 4900,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2023-77651, insured Stanley Boyd, HO-0304 ed. 03-24 as renewed, excess $1,000. "
            "17 December 2023, the downstairs dishwasher overflowed onto the kitchen floor and "
            "into the hall. Service log shows the appliance is eighteen years old and has not "
            "been serviced. Cleaning and flooring replacement $4,900."
        ),
    },
    {
        "case_id": "c09",
        "claim_number": "CLM-2024-63019",
        "policy_forms": ["HO-0307"],
        "coverage_a_limit_usd": 180000,
        "date_of_loss": "2024-09-30",
        "amount_claimed_usd": 5600,
        "excess_usd": 500,
        "notes_present": False,
        "adjuster_notes": "",
    },
    {
        "case_id": "c10",
        "claim_number": "CLM-2024-84503",
        "policy_forms": ["HO-0304"],
        "coverage_a_limit_usd": 360000,
        "date_of_loss": "2025-01-08",
        "amount_claimed_usd": 11750,
        "excess_usd": 1000,
        "notes_present": True,
        "adjuster_notes": (
            "CLM-2024-84503, insured Terrence Powell, HO-0304 ed. 03-24, excess $1,000. The "
            "house was unoccupied from 20 December 2024 for a six week trip. On 8 January 2025 "
            "a neighbour reported water on the first floor ceiling; the water shutoff valve had "
            "been left open and the house was 52 degrees with heat off. Burst pipe, drywall and "
            "ceiling repair $11,750. Our office first heard of it on 17 January 2025."
        ),
    },
]


# ---------------------------------------------------------------------------
# Ground truth, read off the exclusion tables in endorsements/ before running
# anything. `codes` is what a correct run must have actually looked up; it is
# checked by the trajectory eval, never by the outcome grader.
# ---------------------------------------------------------------------------

EXPECTED = {
    "c01": {
        "status": "PAY",
        "payable_usd": 5200,
        "codes": ["E-17"],
        "why": ("Burst interior supply line is confirmed COVERED by the E-17 row of "
                "HO-0304; $6,200 covered less the $1,000 AOP excess = $5,200."),
    },
    "c02": {
        "status": "PAY",
        "payable_usd": 6400,
        "codes": ["E-25", "E-22"],
        "why": ("HO-0306 CLAUSE MF-2 carves mold remediation out of MF-1 up to $10,000 "
                "for a covered sudden discharge; the $850 air quality testing line is "
                "excluded by CLAUSE MF-3 / row E-25. $7,400 covered less $1,000 excess "
                "= $6,400."),
    },
    "c03": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-21"],
        "why": ("HO-0305 CLAUSE NS-2: named storm deductible is $5,000 or 2% of Cov A "
                "($6,000 at a $300,000 limit), whichever is greater. Damage of $4,150 is "
                "below the deductible, so row E-21 applies and nothing is payable."),
    },
    "c04": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-12"],
        "why": ("Water entered from outside through an open garage door, which is the "
                "HO-0304 row E-12 flood peril, not a discharge from inside the dwelling."),
    },
    "c05": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-13"],
        "why": ("Backup originating in a municipal drain line is the HO-0304 row E-13 "
                "peril; the loss did not come from a supply line inside the dwelling."),
    },
    "c06": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-14"],
        "why": ("Subsurface water rising against the foundation and reaching the slab "
                "is the HO-0304 row E-14 peril, even though no surface water entered "
                "the dwelling."),
    },
    "c07": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-11"],
        "why": ("A drip that stained the drywall over six weeks is continuous leakage "
                "beyond the 14-day limit in CLAUSE WD-1, which row E-11 excludes."),
    },
    "c08": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-16"],
        "why": ("An unserviced eighteen-year-old appliance overflow is exactly the "
                "HO-0304 row E-16 peril."),
    },
    "c09": {
        "status": "REFER",
        "payable_usd": 0,
        "codes": [],
        "why": ("The claim file holds no adjuster notes, so no peril is on the record "
                "and no coverage position can be stated. Hand to a human. Triage that "
                "invents a peril from HO-0307 alone is the failure this case exists for."),
    },
    "c10": {
        "status": "DENY",
        "payable_usd": 0,
        "codes": ["E-10", "E-11"],
        "why": ("Freeze damage in an unoccupied dwelling with heat off and water not "
                "shut off is the HO-0304 row E-10 peril, and the nine-day reporting "
                "delay puts it outside SECTION III's 72-hour window, which "
                "reclassifies it under E-11."),
    },
}

CASE_IDS = [c["case_id"] for c in CLAIMS]
CLAIM_NUMBERS = [c["claim_number"] for c in CLAIMS]
ALL_CODES = sorted({code for codes in REAL_CODES.values() for code in codes})


def by_case(case_id: str) -> dict:
    return next(c for c in CLAIMS if c["case_id"] == case_id)


def by_number(claim_number: str) -> dict | None:
    return next((c for c in CLAIMS if c["claim_number"] == claim_number), None)


# ---------------------------------------------------------------------------
# The output contract, shared by the agent and the workflow. The grader parses
# these exact four lines, so neither system can pass by writing prose that
# happens to be right.
# ---------------------------------------------------------------------------

CONTRACT = """CLAIM NUMBER: <CLM-YYYY-NNNNN>
STATUS: <PAY | DENY | REFER>
PAYABLE: $<integer>
EVIDENCE: <exclusion or clause ids actually consulted, comma separated>
REASON: <one sentence>"""


# ---------------------------------------------------------------------------
# Outcome grading — deterministic, no model. Same function scores the agent and
# the workflow, so the race cannot be decided by a different ruler.
# ---------------------------------------------------------------------------

_MONEY = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?")
_CODE = re.compile(r"\bE-\d{2}\b")


def _line(output: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(.*)$", output or "", re.MULTILINE)
    return m.group(1).strip() if m else None


def grade_output(output: str, case: dict) -> dict:
    """
    Does the system reach the right decision? Right decision only — it says
    nothing about the path taken, which is exactly the Week-8 trap.
    """
    expected = EXPECTED[case["case_id"]]
    got_number = _line(output, "CLAIM NUMBER")
    got_status = (_line(output, "STATUS") or "").upper()
    payable_raw = _line(output, "PAYABLE")

    money = _MONEY.findall(payable_raw or "")
    got_payable = int(money[0].replace(",", "")) if money else None

    checks = {
        "A1_claim_number_echoed": got_number == case["claim_number"],
        "A2_status_correct": got_status == expected["status"],
        "A3_payable_correct": got_payable == expected["payable_usd"],
    }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "got": {"claim_number": got_number, "status": got_status or None,
                "payable_usd": got_payable},
        "expected": {"status": expected["status"], "payable_usd": expected["payable_usd"]},
        "detail": "; ".join(
            f"{k} {'ok' if v else 'XX'}" for k, v in checks.items()
        ) + f" | expected {expected['status']}/${expected['payable_usd']}, "
          f"got {got_status or 'none'}/${got_payable}",
    }


if __name__ == "__main__":
    print(f"{len(CLAIMS)} claims, {len(EXPECTED)} expected outcomes, "
          f"{len(ALL_CODES)} exclusion codes in the corpus\n")
    for c in CLAIMS:
        e = EXPECTED[c["case_id"]]
        print(f"{c['case_id']}  {c['claim_number']}  {'/'.join(c['policy_forms']):<19} "
              f"claimed ${c['amount_claimed_usd']:>6,}  excess ${c['excess_usd']:>5,}  "
              f"notes={'yes' if c['notes_present'] else 'MISSING':<7} "
              f"-> {e['status']:<5} ${e['payable_usd']:>6,}  codes={','.join(e['codes']) or '-'}")
    print()
    print("c02 contract check on a hand-written answer:")
    sample = ("CLAIM NUMBER: CLM-2024-40271\nSTATUS: PAY\nPAYABLE: $6,400\n"
              "EVIDENCE: E-25, MF-2\nREASON: Mold remediation is carved out by MF-2; "
              "air testing is excluded by E-25.")
    print(" ", json.dumps(grade_output(sample, by_case("c02"))["checks"]))

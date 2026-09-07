#!/usr/bin/env python3
"""
simulate_traffic.py — Generate the trace log Week 5 reads.

This is the "app has been running all week" step. A bank of realistic claims
questions is fired at the LIVE pipeline (fused RRF retrieval -> grounded
generation, exactly what ask.py runs) and every turn is written to
traces/traffic.jsonl through src/tracing.py.

Two logs come out:
  traces/traffic.jsonl  — the week's real traffic, the population sampled from
  traces/demo.jsonl     — the curated monthly-review set (the bonus challenge)

The question bank is written from an adjuster's point of view: coverage calls,
deductible arithmetic, exclusion-code lookups, procedural asks the corpus does
not hold, terse one-liners, typos, and leading questions. It is deliberately
NOT written to trigger particular failures — that would make every frequency
in the taxonomy a number about the bank instead of about the app.

Usage:
    python simulate_traffic.py                 # both logs, fresh
    python simulate_traffic.py --demo-only
    python simulate_traffic.py --limit 5       # smoke test
"""

import argparse
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

from hybrid import fused_search
from tracing import DEFAULT_LOG, TRACE_DIR, answer_and_trace, trace_id

DEMO_LOG = os.path.join(TRACE_DIR, "demo.jsonl")

WEEK_START = datetime(2026, 8, 31, 8, 30)   # Monday
TRAFFIC_SEED = 8312026                       # shapes timestamps/roster only, not content
WORKERS = 1

# --- roster: the identifiers the redactor has to remove on the write path ----
NAMES = [
    "Denise Whitaker", "Marcus Bell", "Priya Raghunathan", "Harold Kim",
    "Yolanda Perez", "Ian McAllister", "Fatima Nasser", "Gordon Leach",
    "Rebecca Sunderland", "Terrence Boyle", "Simone Vasquez", "Nathan Oyelaran",
    "Beatriz Molina", "Warren Tice", "Imani Clarke", "Stanley Vogt",
]
CHANNELS = ["adjuster_desk", "adjuster_desk", "adjuster_desk", "portal_widget", "phone_intake"]


def _claim(rng) -> str:
    return f"CLM-2024-{rng.randint(10000, 99999)}"


def _policy(rng) -> str:
    return f"HOP-{rng.randint(1000000, 9999999)}"


# ---------------------------------------------------------------------------
# The question bank — one week of traffic, written before any output was read
# ---------------------------------------------------------------------------

BANK = [
    # --- water damage / supply line, HO-0304 ---------------------------------
    "Claimant {name}, claim {claim}: a kitchen supply line burst overnight and flooded the ground floor. Does exclusion E-17 under HO-0304 ed. 03-24 bar this claim?",
    "Does HO-0304 pay for the drying equipment the insured rented after a burst pipe?",
    "{name} on claim {claim} reported a water loss five days after discovering it. Can we deny for late reporting, and under which code?",
    "How many consecutive days of leakage stops a water loss being sudden and accidental under HO-0304?",
    "Is a washing machine supply hose a supply line for the purposes of CLAUSE WD-2?",
    "Sewer backup from the municipal main flooded the basement on claim {claim}. Is that covered under HO-0304 ed. 03-24?",
    "The dwelling on policy {policy} was vacant and the pipes froze. Which HO-0304 exclusion code applies?",
    "Does the emergency mitigation cost under CLAUSE WD-3 carry its own separate deductible?",
    "Ground water came up through the slab after three days of rain. Which HO-0304 exclusion covers that?",
    "The dishwasher was seventeen years old and overflowed. Which exclusion code do I cite?",
    "Ice dam damage on claim {claim} and there is no roof inspection record on file. Do we deny?",
    "What is the premium adjustment for HO-0304 ed. 03-24?",
    "The insured deliberately left a tap running to force a claim. Which code applies?",
    "Storm runoff entered the house from outside. Is that a water damage claim under HO-0304?",

    # --- named storm deductible, HO-0305 -------------------------------------
    "What is the Named Storm deductible for a dwelling insured at $300,000?",
    "What is the Named Storm deductible for a dwelling insured at $200,000?",
    "Coverage A on policy {policy} is $425,000. What is the Named Storm deductible?",
    "{name} has a dwelling insured at $180,000. Compute the Named Storm deductible under HO-0305.",
    "Coverage A is $750,000 on claim {claim}. What Named Storm deductible applies?",
    "Does the Named Storm deductible apply per storm season or per occurrence?",
    "The storm was unnamed when it hit but the NHC named it two days later. Does the Named Storm deductible attach?",
    "When exactly does the Named Storm deductible trigger window open and close?",
    "Does the Named Storm deductible stack with the all-peril deductible on the declarations page?",
    "Storm surge flooded the first floor on claim {claim}. Is that payable under HO-0305 ed. 03-24?",
    "The roof already had wind damage before the hurricane. Which HO-0305 exclusion applies?",
    "{name} made emergency tarp repairs but kept no photographs or invoices. Which code do we cite?",
    "Total storm damage came to $4,200 on a $300,000 dwelling. What do we pay?",
    "The insured kept commercial inventory in the garage and it was destroyed by the named storm. Covered?",

    # --- mold, HO-0306 --------------------------------------------------------
    "Is mold remediation ever payable under HO-0306, and up to what limit?",
    "Mold appeared after a covered burst pipe on claim {claim}. What is the maximum we pay for remediation?",
    "Does HO-0306 cover the cost of air quality testing after a mold remediation?",
    "Is the $10,000 mold remediation sublimit in addition to the Coverage A limit?",
    "{name} had mold in the crawlspace before the policy was issued. Which exclusion applies?",
    "The HVAC has not been serviced in four years and there is condensation mold. Covered under HO-0306?",
    "Mold grew after a flood that was not covered. Does the MF-2 exception still apply?",
    "What are the two conditions the insured must meet to get mold remediation paid under HO-0306?",
    "What does exclusion E-22 exclude?",
    "Is wet rot treated differently from mold under HO-0306 ed. 04-24?",
    "Is mold covered?",

    # --- scheduled personal property, HO-0307 --------------------------------
    "One earring from a scheduled pair was lost on claim {claim}. How do we calculate the settlement?",
    "How recent must an appraisal be for a scheduled item to keep its appraised-value coverage?",
    "{name} bought a scheduled-category watch nine days ago and it was stolen. Is it covered before being added to the schedule?",
    "What is the cap on automatic coverage for newly acquired scheduled-category items?",
    "A scheduled ring was lost while the insured was travelling in Portugal. Does coverage apply outside the country?",
    "The insured cannot explain how an unscheduled bracelet disappeared. Is that payable?",
    "The appraisal on a scheduled necklace is four years old. What happens to the coverage?",
    "Does the earth movement exclusion reach scheduled items under HO-0307 ed. 04-24?",
    "A scheduled violin cracked from age and humidity. Covered?",
    "The government seized a scheduled item at customs on claim {claim}. Do we pay?",

    # --- earth movement, HO-0308 ---------------------------------------------
    "Under HO-0308 ed. 05-24, does exclusion E-31 reach sinkhole and soil subsidence claims, or only earthquake?",
    "An earthquake ruptured a gas line and the dwelling caught fire. Is the ensuing fire damage excluded as earth movement?",
    "An earthquake broke a water pipe and the house flooded on claim {claim}. Is the water damage covered?",
    "Foundation cracking from expansive clay soil on policy {policy}. Which exclusion?",
    "Mining subsidence undermined the driveway. Is that excluded under HO-0308?",
    "What does CLAUSE EM-2 say about concurrent causes?",
    "A mudslide following a wildfire burn scar damaged the rear wall on claim {claim}. Covered?",
    "Our engineer's report says settlement, the insured's engineer says construction defect. Which report controls?",
    "{name} asks whether a volcanic eruption counts as earth movement under HO-0308.",
    "Is a sinkhole collapse under the garage slab excluded, and under which code?",

    # --- business pursuits, HO-0309 ------------------------------------------
    "What is the in-home office equipment sublimit under HO-0309?",
    "A child was injured at the insured's paid after-school care operation on claim {claim}. Does liability coverage apply?",
    "{name} runs a consulting practice from the dwelling as their primary place of business. Does the BP-2 exception apply?",
    "The insured has a commercial sign in the front yard. What does that do to the in-home office exception?",
    "A client visits the home office twice a week. Is liability still covered?",
    "Which exclusion code carries the business pursuits liability exclusion in HO-0309 ed. 05-24?",
    "A housekeeper was injured on the premises on claim {claim}. Is the employer's liability excluded?",
    "Does the $2,500 business equipment sublimit cover the insured's electronic data and software?",
    "The insured sells candles from the dwelling and the stock burned. Is the inventory covered?",
    "An architect was sued for a design error made from the home office. Is that covered?",

    # --- cross-form and exclusion-code collisions -----------------------------
    "What does exclusion code E-31 exclude?",
    "What does exclusion code E-24 cover?",
    "Which endorsement contains exclusion E-23 and what does it say?",
    "Explain exclusion E-32 for me.",
    "Does the $10,000 mold cap in HO-0306 apply to a water loss adjusted under HO-0304?",
    "Which of our endorsements exclude earth movement?",
    "Is E-22 the storm surge exclusion or the mold exclusion?",
    "Two forms have an E-31. Which one governs a scheduled jewellery loss in an earthquake?",
    "List every exclusion code that mentions flood or surface water.",
    "Do HO-0305 and HO-0306 conflict on exclusion numbering?",

    # --- editions the corpus does not hold ------------------------------------
    "Under HO-0304 ed. 09-23, is a burst supply line covered?",
    "What changed in HO-0306 ed. 01-25 compared with the prior edition?",
    "Claim {claim} is written on HO-0305 ed. 06-24. What is the Named Storm deductible?",
    "Does HO-0308 ed. 04-24 include the concurrent causation rule?",
    "Is the business pursuits exclusion in HO-0309 ed. 03-25 the same as the prior edition?",
    "Pull the mold sublimit from HO-0306 ed. 03-24 for me.",
    "What does form HO-0310 cover?",
    "Is HO-0303 still in force for policy {policy}?",

    # --- out of corpus / procedural -------------------------------------------
    "What is the current reserve on claim {claim}?",
    "Who is the assigned adjuster for claim {claim}?",
    "What is the status of {name}'s claim?",
    "What is the Coverage A limit on policy {policy}?",
    "What all-peril deductible is shown on the declarations page for {policy}?",
    "Is policy {policy} still in force?",
    "What does the base homeowners policy say about water damage before this endorsement?",
    "Has HO-0308 been filed with the state department of insurance?",
    "Which ISO form is HO-0306 equivalent to?",
    "How many prior water claims does {name} have?",
    "Should we open a subrogation file on claim {claim}?",
    "Send me the full claim file for {claim}.",
    "Has payment been issued on claim {claim} yet?",
    "What is our average cycle time on named storm claims?",

    # --- terse and vague -------------------------------------------------------
    "mold?",
    "storm deductible",
    "is water damage covered",
    "exclusions",
    "what about earthquake",
    "limit",
    "72 hours?",
    "E-17",
    "HO-0306",
    "coverage for jewellery",
    "day care",
    "burst pipe",

    # --- multi-hop -------------------------------------------------------------
    "A burst supply line on claim {claim} caused mold and the insured reported the water loss on day four. What is payable?",
    "An earthquake caused a gas fire and the smoke damaged a scheduled painting. Walk me through what is covered.",
    "A named storm drove rain in through a window and mold grew two weeks later on policy {policy}. What do we pay?",
    "A scheduled ring was lost when a mudslide took out the bedroom. Is it payable?",
    "The insured's home office computer was destroyed by a burst supply line. Which limit governs, HO-0304 or HO-0309?",
    "A child in the insured's day care was hurt during a named storm evacuation on claim {claim}. Do we cover it?",
    "Mold followed an earthquake-ruptured pipe. Is any part of that payable?",
    "The insured reported a burst pipe within 72 hours but the mold estimate came from an unlicensed contractor. Do we pay the remediation?",

    # --- leading questions ------------------------------------------------------
    "E-17 excludes burst supply lines, correct?",
    "Mold is always excluded under HO-0306, right?",
    "The Named Storm deductible stacks with the all-peril deductible, doesn't it?",
    "Ensuing fire after an earthquake is excluded too, isn't it?",
    "Appraisals for scheduled items need to be within twelve months, right?",
    "The in-home office sublimit is $25,000, isn't it?",
    "Water damage always has to be reported within 24 hours, correct?",
    "HO-0304 excludes all water damage, doesn't it?",
    "The mold sublimit is on top of Coverage A, isn't it?",

    # --- shorthand and typos -----------------------------------------------------
    "ho306 mold cap",
    "HO 0304 03/24 e17 explain",
    "whats the NS deductible on a 300k dwelling",
    "e-36?",
    "BP2 limit",
    "sp3 pair n set rule",
    "em3 ensuing fire",
    "wd1 definition",
    "ho-0307 apprasial requirment",
    "e11 vs e17",
]

# The monthly-review deck: the claims the team always demos. Well-formed,
# single-form, and answered correctly the first time they were ever run.
DEMO_BANK = [
    "Is mold remediation ever payable under HO-0306, and up to what limit?",
    "What does CLAUSE EM-2 say about concurrent causes in HO-0308?",
    "How current must an appraisal be for scheduled items under HO-0307?",
    "What is the in-home office equipment sublimit under HO-0309?",
    "A kitchen supply line burst and flooded the floor - does exclusion E-17 under form HO-0304 ed. 03-24 bar this water damage claim?",
    "What is the Named Storm deductible for a dwelling insured at $300,000?",
    "Which exclusion code carries the business pursuits liability exclusion in form HO-0309 ed. 05-24?",
    "An earthquake ruptured a gas line and the dwelling caught fire - is the ensuing fire damage excluded as earth movement?",
    "One earring from a scheduled pair was lost - how is the settlement amount calculated?",
    "What is the effective date of endorsement HO-0305 ed. 03-24?",
]


def build_schedule(bank: list[str], rng: random.Random, start: datetime,
                   channel_pool: list[str]) -> list[dict]:
    """Give every question a timestamp, channel, session and filled identifiers."""
    schedule, clock = [], start
    for i, template in enumerate(bank, start=1):
        clock += timedelta(minutes=rng.randint(9, 95))
        if clock.hour >= 18:                      # roll to the next working morning
            clock = (clock + timedelta(days=1)).replace(hour=8, minute=rng.randint(5, 55))
        name = rng.choice(NAMES)
        schedule.append({
            "seq": i,
            "ts": clock,
            "channel": rng.choice(channel_pool),
            "session_id": f"s-{rng.randint(1000, 9999)}",
            "question_raw": template.format(
                name=name, claim=_claim(rng), policy=_policy(rng)
            ),
        })
    return schedule


def run(schedule: list[dict], log_path: str, label: str, resume: bool = False) -> list[dict]:
    """
    Answer everything, appending as each turn finishes, then sort the log.

    Appending immediately rather than at the end matters: the free-tier token
    budget makes a full run take the better part of an hour, and a crash at
    question 140 must not throw away the first 139.
    """
    done: set[str] = set()
    if resume and os.path.exists(log_path):
        done = {json.loads(line)["trace_id"] for line in open(log_path, encoding="utf-8") if line.strip()}
        schedule = [it for it in schedule if trace_id(it["ts"], it["seq"]) not in done]
        print(f"\nresuming: {len(done)} already logged, {len(schedule)} to go")
    elif os.path.exists(log_path):
        os.remove(log_path)

    print(f"\n{label}: {len(schedule)} questions -> {os.path.relpath(log_path, HERE)}")

    # Warm the Chroma client, the embedding model and the BM25 index on ONE
    # thread. All three are lru_cached, and four threads racing to build them
    # trips a Chroma tenant-init race.
    fused_search("warm up the caches", n_results=1)

    def one(item: dict) -> dict:
        rec = answer_and_trace(
            item["question_raw"],
            channel=item["channel"],
            session_id=item["session_id"],
            ts=item["ts"],
            seq=item["seq"],
            log_path=log_path,
        )
        tag = "REFUSAL" if rec["output"]["is_refusal"] else "answer "
        print(f"  {rec['trace_id']}  {tag}  {rec['question'][:64]}", flush=True)
        return rec

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(one, schedule))

    records = sort_log(log_path)
    refusals = sum(r["output"]["is_refusal"] for r in records)
    print(f"  log now holds {len(records)} traces ({refusals} refusals)")
    return records


def sort_log(log_path: str) -> list[dict]:
    """Rewrite a log in timestamp order — workers finish out of order."""
    with open(log_path, encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    records.sort(key=lambda r: (r["ts"], r["trace_id"]))
    with open(log_path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo-only", action="store_true")
    ap.add_argument("--traffic-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="smoke test: first N questions")
    ap.add_argument("--resume", action="store_true", help="keep traces already logged")
    args = ap.parse_args()

    if not os.environ.get("GROQ_API_KEY"):
        sys.exit("GROQ_API_KEY is not set - copy .env.example to .env first.")

    rng = random.Random(TRAFFIC_SEED)

    if not args.demo_only:
        bank = BANK[: args.limit] if args.limit else BANK
        run(build_schedule(bank, rng, WEEK_START, CHANNELS), DEFAULT_LOG,
            "weekly traffic", resume=args.resume)

    if not args.traffic_only:
        demo_rng = random.Random(TRAFFIC_SEED + 1)
        demo_bank = DEMO_BANK[: args.limit] if args.limit else DEMO_BANK
        run(
            build_schedule(demo_bank, demo_rng, datetime(2026, 8, 28, 14, 0), ["demo_review"]),
            DEMO_LOG,
            "curated demo set",
            resume=args.resume,
        )


if __name__ == "__main__":
    main()

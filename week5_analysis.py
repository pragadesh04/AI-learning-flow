import argparse
import csv
import difflib
import json
import os
import random
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

TRACE_DIR = os.path.join(HERE, "traces")
TRAFFIC_LOG = os.path.join(TRACE_DIR, "traffic.jsonl")
DEMO_LOG = os.path.join(TRACE_DIR, "demo.jsonl")

RULE = "=" * 78


def load(log_path: str) -> list[dict]:
    with open(log_path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_id(traces: list[dict]) -> dict[str, dict]:
    return {t["trace_id"]: t for t in traces}


# ---------------------------------------------------------------------------
# sample — seeded, over the whole population, provable after the fact
# ---------------------------------------------------------------------------

def cmd_sample(args) -> None:
    traces = load(args.log)
    population = sorted(t["trace_id"] for t in traces)   # sorted: order-independent
    rng = random.Random(args.seed)
    picked = sorted(rng.sample(population, args.n))

    out = {
        "log": os.path.relpath(args.log, HERE).replace("\\", "/"),
        "population_size": len(population),
        "seed": args.seed,
        "n": args.n,
        "selection_rule": (
            "random.Random(seed).sample(sorted(trace_ids), n) — Python 3.13 "
            "stdlib Mersenne Twister; sorting the population first makes the "
            "draw independent of the order lines were written to the log"
        ),
        "trace_ids": picked,
    }
    path = args.out or os.path.join(TRACE_DIR, f"sample_seed{args.seed}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)

    print(f"population : {len(population)} traces in {out['log']}")
    print(f"seed       : {args.seed}")
    print(f"drew       : {args.n}")
    print(f"written to : {os.path.relpath(path, HERE)}\n")
    for tid in picked:
        print(" ", tid)


# ---------------------------------------------------------------------------
# show — the reading view used for open coding
# ---------------------------------------------------------------------------

def render(trace: dict, full: bool = True) -> str:
    ret, out = trace["retrieval"], trace["output"]
    lines = [
        RULE,
        f"{trace['trace_id']}   {trace['ts']}   {trace['channel']}   "
        f"schema v{trace['schema_version']}",
        RULE,
        f"Q: {trace['question']}",
        f"   redaction: {trace['redaction']['counts'] or 'none'} "
        f"({trace['redaction']['stage']})",
        "",
        f"retrieved ({ret['mode']}, k={ret['n_results']}, {ret['latency_ms']} ms):",
    ]
    for h in ret["hits"]:
        lines.append(
            f"   {h['rank']}. {h['chunk_id']:<24s} score={h['score']:.5f} "
            f"dense={str(h['dense_rank']):>4s} bm25={str(h['bm25_rank']):>4s}  "
            f"{h['form_number']} ed.{h['edition_date']}  {h['clause_id']}"
        )
    forms = Counter(h["form_number"] for h in ret["hits"])
    lines += [
        f"   forms in context: {dict(forms)}",
        "",
        f"model: {trace['model']['name']} temp={trace['model']['temperature']} "
        f"max_tokens={trace['model']['max_tokens']}  ({out['latency_ms']} ms)",
        f"refusal: {out['is_refusal']}",
        "",
        "OUTPUT:",
        out["raw"] if full else out["raw"][:400],
        "",
    ]
    return "\n".join(lines)


def cmd_show(args) -> None:
    traces = by_id(load(args.log))
    if args.sample:
        with open(args.sample, encoding="utf-8") as fh:
            ids = json.load(fh)["trace_ids"]
    else:
        ids = args.trace_ids
    for tid in ids:
        if tid not in traces:
            print(f"!! {tid} not in {args.log}")
            continue
        print(render(traces[tid]))


# ---------------------------------------------------------------------------
# replay — rebuild the request from the trace and re-run it
# ---------------------------------------------------------------------------

def cmd_replay(args) -> None:
    from replay import replay_trace

    traces = by_id(load(args.log))
    if args.trace_id not in traces:
        sys.exit(f"{args.trace_id} not found in {args.log}")
    replay_trace(traces[args.trace_id], live=not args.dry_run)


# ---------------------------------------------------------------------------
# tally — turn the hand-written coding file into the taxonomy's numbers
# ---------------------------------------------------------------------------

SEVERITY_ORDER = {"wrongly denies or pays": 0, "misleads the adjuster": 1, "annoys the adjuster": 2}


def cmd_tally(args) -> None:
    with open(args.coding, encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("trace_id", "").strip()]

    total = len(rows)
    modes = Counter(r["mode"].strip() for r in rows)
    severity = {r["mode"].strip(): r.get("severity", "").strip() for r in rows}
    example = {}
    for r in rows:                                   # first trace_id per mode
        example.setdefault(r["mode"].strip(), r["trace_id"].strip())

    print(f"coded traces: {total}   distinct modes: {len(modes)}\n")
    print(f"| {'Mode':<52s} | Count | Freq % | Severity | Example trace_id |")
    print(f"|{'-' * 54}|-------|--------|----------|------------------|")
    for mode, count in sorted(
        modes.items(),
        key=lambda kv: (-kv[1], SEVERITY_ORDER.get(severity.get(kv[0], ""), 9)),
    ):
        print(
            f"| {mode:<52s} | {count:>5d} | {100 * count / total:>5.0f}% "
            f"| {severity.get(mode, '?'):<8s} | {example[mode]} |"
        )
    print(f"\ncheck: counts sum to {sum(modes.values())} of {total}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sample", help="seeded random draw over a trace log")
    s.add_argument("--log", default=TRAFFIC_LOG)
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--n", type=int, default=20)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_sample)

    s = sub.add_parser("show", help="print traces in the open-coding reading view")
    s.add_argument("trace_ids", nargs="*")
    s.add_argument("--log", default=TRAFFIC_LOG)
    s.add_argument("--sample", default=None, help="a sample json written by `sample`")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("replay", help="rebuild one trace's request and re-run it")
    s.add_argument("trace_id")
    s.add_argument("--log", default=TRAFFIC_LOG)
    s.add_argument("--dry-run", action="store_true", help="reconstruct only, no API call")
    s.set_defaults(func=cmd_replay)

    s = sub.add_parser("tally", help="count modes from the hand-written coding csv")
    s.add_argument("--coding", default=os.path.join(TRACE_DIR, "coding.csv"))
    s.set_defaults(func=cmd_tally)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

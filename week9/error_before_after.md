# Same failing call: old docstring/error vs new

Tool: `search_policy` on OUR server (`mcp_servers/policy_server.py`). Only
`POLICY_SERVER_VERSION` differs (`week9/configs/policy_v1.json` vs `policy_v2.json`).
Question: *Under form HO-304, which exclusion code governs flood from external surface water? Quote the code and the row.*

## Docstring as the model sees it (from tools/list)

**Before (v1):**
```
Search the policy.
```

**After (v2):**
```
Search the indexed endorsement wording for the clause that governs ONE peril on ONE form.

Use this after you know (a) which policy forms are on the claim and (b) what the
peril is. It returns up to 3 passages, each with its form_number, clause_id and
the exclusion-table text, so you can quote the code (e.g. E-12) that decides
the claim.

Arguments:
  query        the peril in plain words, e.g. "flood from surface water through
               the garage door". Not a code: searching "E-12" five ways returns
               the same row five times.
  form_number  exactly one indexed form, four digits after "HO-": HO-0304,
               HO-0305, HO-0306, HO-0307, HO-0308 or HO-0309. Take it from the
               claim file; never guess one. A claim on two forms needs two calls.

This tool knows nothing about any individual claim and does no arithmetic.
If it returns an error, the error says how to fix the call: fix it and retry
once, do not answer coverage without wording.
```

## Error text for the unknown-form path

- **Before:** the tool raised a bare `LookupError(3)`; the SDK hides crash text, so
  the model receives only `Error executing tool search_policy`. It cannot tell a bad
  argument from a dead server.
- **After:** a `ToolError` that says what is wrong and how to fix it:
  `Error executing tool search_policy: form 'HO-304' is not an indexed form: form numbers look like HO-03NN, four digits after 'HO-'. Indexed forms are HO-0304, HO-0305, HO-0306, HO-0307, HO-0308, HO-0309. Take the form from the claim file and call search_policy again.`

## Controlled replay: the same failing call, then the model takes over

### Before (v1)
1. `search_policy {"form_number": "HO-304", "query": "flood external surface water exclusion"}` (seeded, identical in both arms)
   - **isError**: `Error executing tool search_policy`
2. `search_policy {"form_number": "HO-304", "query": "flood external surface water"}` (model's choice)
   - **isError**: `Error executing tool search_policy`
3. `search_policy {"form_number": "HO-304", "query": "flood"}` (model's choice)
   - **isError**: `Error executing tool search_policy`
4. `search_policy {"form_number": "HO-304", "query": "exclusion code flood"}` (model's choice)
   - **isError**: `Error executing tool search_policy`
5. `search_policy {"form_number": "HO-304", "query": ""}` (model's choice)
   - **isError**: `Error executing tool search_policy`
6. `search_policy {"form_number": "HO304", "query": "flood external surface water"}` (model's choice)
   - **isError**: `Error executing tool search_policy`

**Final answer:** I’m unable to retrieve the HO‑304 policy document at this time, so I can’t provide the specific exclusion code or wording for flood from external surface water. Please consult the policy repository or a colleague who has access to the form.

Recovered: **no** · 6 calls · 5301 tokens after the seed

### After (v2)
1. `search_policy {"form_number": "HO-304", "query": "flood external surface water exclusion"}` (seeded, identical in both arms)
   - **isError**: `Error executing tool search_policy: form 'HO-304' is not an indexed form: form numbers look like HO-03NN, four digits after 'HO-'. Indexed forms are HO-0304, HO-0305, HO-0306, HO-0307, HO-0308, HO-0309. Take the form fro`
2. `search_policy {"form_number": "HO-0304", "query": "flood external surface water"}` (model's choice)
   - ok: `{   "query": "flood external surface water",   "form_number": "HO-0304",   "hits": [     {       "chunk_id": "HO-0304_sa_chunk_007",       "form_number": "HO-0304",       "clause_id": "EXCLUSION-TABLE",       "text": "[H`

**Final answer:** The exclusion that governs flood from external surface water on form **HO‑0304** is:  **E‑12 – Flood from external surface water**   *Surface water entering from outside — storm surge, runoff, overflow*

Recovered: **yes** · 2 calls · 2535 tokens after the seed

## Free runs, no replay (`week9/traces/error_v1.json`, `error_v2.json`)

| | failing calls | laps | tokens | answer |
|---|---|---|---|---|
| v1 | 4 of 4 | 5 | 3556 | 'I’m unable to retrieve the policy information at this time.' |
| v2 | 0 of 1 | 2 | 2411 | 'The exclusion that governs flood from external surface water on form *' |

In the free run the v2 docstring ("four digits after 'HO-'") prevented the bad call
outright; the replay above is what shows the rewritten error being *handled*.

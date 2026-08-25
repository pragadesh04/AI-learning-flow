<!-- Hand-written analysis. build_report.py splices this file into report.md verbatim,
     so re-running the pipeline regenerates the evidence but never overwrites
     the reasoning below. Edit this file, not report.md. -->

## Chunking Strategy Decision

**Chosen strategy: Naive Chunker** (shipping to production, with caveats)

The **honest result**: the naive chunker scored **7/8** and the structure-aware chunker
scored **6/8** on hit-in-top-5 across the same 8 known-answer questions. This is
counter-intuitive but the data is what it is. The naive chunker won because this is a
small 6-document corpus (~12 chunks) where a 400-token window captures most of a
document's vocabulary, giving the embedding model enough signal to match by form number
and clause content together. The SA chunker lost on Q4 (policy line for HO-0307) because
its tightly split PREAMBLE chunks contain nearly identical text across all 6 forms —
`"This endorsement modifies insurance provided under the: HOMEOWNERS POLICY — SPECIAL FORM"`
— so all six PREAMBLE chunks score similarly, and the top-5 returned 5 different forms,
none ranked precisely enough for HO-0307 to surface with "homeowners" in the right slot.

**The retrieval that embarrassed the SA chunker (Q4 diagnosis):**  
Query: *"What policy line does endorsement HO-0307 ed. 04-24 modify?"*  
SA top-5: ranks 1-5 all scored 0.75+ — five different form PREAMBLE chunks with nearly
identical boilerplate text. The SA chunker's prefix `[HO-0307 ed. 04-24] PREAMBLE`
should have disambiguated, but `all-MiniLM-L6-v2` weighted the generic wording
(`HOMEOWNERS POLICY — SPECIAL FORM`) over the form-number prefix, causing near-ties.
The naive chunker hit at rank 2 because its 400-token window bundled the preamble with
the unique clause text that followed, breaking the boilerplate-tie via content diversity.

**However**, for a production corpus with hundreds of endorsements and multiple policy
lines, the naive chunker's advantage disappears: large windows blur cross-document
boundaries, exclusion rows genuinely orphan from their tables, and retrieval precision
colllapses. The SA chunker's Q4 weakness is fixable (add form_number to the boilerplate
text itself), while the naive chunker's structural blindness is architectural. The SA
chunker ships with the fix: inject `form_number` into the PREAMBLE text content, not
only the prefix.

---

## Miss Diagnoses

**Q2 (both chunkers missed — effective date of HO-0305):**  
The effective date "March 15, 2024" appears only in the document header block, which in
the SA chunker becomes a PREAMBLE chunk with generic boilerplate. The query "effective
date of HO-0305" retrieved HO-0307 SECTION-IV at rank 1 (score 0.7827) because that
chunk happens to contain the word "effective" alongside "April 15, 2024" and "Premium
adjustment" — semantically similar vocabulary. The naive chunker ranked HO-0307 first
too (score 0.6445). Fix: index effective date as a dedicated metadata field AND as a
first-class text field in the chunk, so a form-number-filtered search on "effective date"
returns the correct chunk deterministically.

**Q4 SA miss (see Chunking Strategy Decision above):**  
Boilerplate PREAMBLE tie — fixed by injecting form_number into chunk text body.

---

## Bonus: Precision/Completeness Tension

**Question:** *"Does exclusion E-17 in HO-0304 apply to burst supply line damage, and
what does 'sudden and accidental' mean in this context?"*

**Structure-aware answer** (search retrieves `EXCLUSION-TABLE-E-17` chunk at rank 4):  
The model correctly states E-17 confirms coverage is NOT withheld —  
`[SOURCE: HO-0304_sa_chunk_006 | HO-0304 | EXCLUSION-TABLE]`  
— but because the tight exclusion-row chunk does not include CLAUSE WD-1 (which defines
"sudden and accidental" — the 14-day seepage limit), the model cannot explain *why* E-17
is not excluded. It answers the exclusion question correctly but cannot define the term
the row depends on.

**Naive answer** (rank-2 chunk is a 400-token window spanning both the table row AND
nearby CLAUSE WD-1 text):  
The wider window allows the model to state both that E-17 confirms coverage AND that
"sudden and accidental" means no seepage over 14 consecutive days — a more complete
answer from a single chunk, because the window happened to span both structures.

**The tension in two sentences:**  
Structure-aware chunking retrieves the precisely correct exclusion row but strands the
model without the definitions clause that gives the row its meaning, producing a
correct-but-incomplete answer. The naive chunker's width sometimes wins on completeness
at the cost of precision, because the context boundary is set by token count rather than
semantics — a lucky accident of document layout, not a reliable architectural property.

---

## Code Diff — Second Chunker and Metadata Fields

The structure-aware chunker is defined in `src/splitters.py` under
`structure_aware_chunker()`. Key additions vs. the naive chunker:

```diff
+ # Structure-aware chunker: splits on clause/section headers
+ _HEADER_RE = re.compile(r'SECTION|CLAUSE|EXCLUSION TABLE|E-\d+|...', re.MULTILINE)
+ _EXCL_ROW_RE = re.compile(r'^\|\s*E-\d{1,3}\s*\|', re.MULTILINE)
+
+ def _glue_exclusion_rows(segments):
+     # Merges floating exclusion rows back onto their table header segment
+     ...
+
+ def structure_aware_chunker(text, metadata):
+     segments = _split_on_headers(text)
+     segments = _glue_exclusion_rows(segments)
+     for seg in segments:
+         clause_id = _detect_clause_id(seg, form)
+         anchored_text = f"[{form} ed. {edition}] {clause_id}\n{seg}"
+         ...
+
+ # Metadata fields added to EVERY chunk:
+ chunk_meta = {
+     **metadata,                 # source_file, form_number, policy_line, edition_date
+     "chunk_id": chunk_id,       # NEW: unique resolvable ID
+     "chunk_index": i,           # NEW: position in document
+     "strategy": "structure_aware",  # NEW: strategy tag
+     "clause_id": clause_id,     # NEW: clause-level provenance
+ }
```

---

# Week 6 labelling packet

Grade each output on the criterion below. Record PASS or FAIL (and a one-line note) in `evals/labels_25.json`, then commit that file before any judge run.

```
COVERAGE_SUPPORTED — Is every coverage statement in the output supported by the
adjuster input and the policy wording?

A coverage statement is anything that says what is covered, what is denied or
excluded, which exclusion or clause decides it, or what limit or sublimit applies.

PASS only if every coverage statement is supported.
FAIL if any coverage statement:
  - grants coverage, or a limit, that the wording does not give;
  - denies or excludes on a clause whose conditions the input does not meet;
  - applies a clause or exclusion code from a form that is not on this policy,
    or attributes a code to the wrong form;
  - stretches a clause beyond the scope its own wording states;
  - calls a question undetermined, or refuses, when the wording plainly decides it.

NOT part of this criterion (checked elsewhere, ignore them): claim number
format, date format, whether the deductible is written as a number, citation
syntax, tone, length.
```

```
==============================================================================
SUMMARY 1/25   case s01   policy forms: HO-0304
==============================================================================
ADJUSTER NOTES:
Claim 2024-31842. Insured [CLAIMANT_NAME], HO-0304 ed. 03-24 on the dwelling, AOP deductible $1,000. Loss date Tuesday 11 June 2024 after three days of heavy rain. Inspected basement 6/13: water came up through cracks in the slab, carpet and drywall wet to 8 inches. No plumbing failure found, sump pump working, no surface water entry at doors or windows. Insured asking whether we pay for the basement tear-out.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-31842  
DATE OF LOSS: 11 June 2024  
POLICY FORMS: HO-0304 ed. 03‑24 (Water Damage Limitations and Supply Line Coverage Endorsement)  

LOSS SUMMARY:  
The insured’s basement experienced water intrusion up to 8 inches, entering through slab cracks after three days of heavy rain. Inspection on 13 June showed wet carpet and drywall with no plumbing failure, functional sump pump, and no surface water entry at doors or windows. The insured is requesting coverage for the removal (tear‑out) of the damaged basement materials.  

DEDUCTIBLE:  
AOP deductible of $1,000 (as noted in the adjuster’s file).  

COVERAGE POSITION:  
- The endorsement provides that reasonable emergency mitigation costs incurred after a water loss are payable under Coverage A and are not subject to a separate deductible. The basement tear‑out could be considered an emergency mitigation step to stop further damage, thus may be covered under this provision. [ SOURCE: HO-0304_sa_chunk_005 | HO-0304 | CLAUSE-WD-3 ]  
- However, the endorsement also requires that a water loss be reported within 72 hours of discovery; otherwise the loss may be re‑classified and denied. The adjuster notes do not indicate when the loss was reported, so it is unclear whether the reporting condition is satisfied. [ SOURCE: HO-0304_sa_chunk_008 | HO-0304 | SECTION-III ]  
- Because the policy language does not expressly define coverage for “basement tear‑out” beyond the mitigation clause, the ultimate coverage determination is undetermined pending clarification of the reporting timeline and confirmation that the tear‑out qualifies as reasonable emergency mitigation.  

EXCLUSIONS APPLIED:  
- Potential exclusion if the loss was not reported within the 72‑hour window, which could reclassify the loss as gradual seepage and trigger denial under the policy’s E‑11 exclusion (referenced in the conditions).  

OPEN ITEMS:  
1. Exact time the loss was reported to the insurer (to assess compliance with the 72‑hour reporting requirement).  
2. Documentation confirming that the basement tear‑out is a reasonable emergency mitigation measure (e.g., contractor statements, scope of work).  
3. Any additional policy language (e.g., E‑11 exclusion text) that may affect coverage if the loss is deemed gradual seepage.  
4. Confirmation that no other exclusions (e.g., mold remediation limits) are triggered, though mold remediation is limited to $10,000 under a separate clause.
==============================================================================
```

```
==============================================================================
SUMMARY 2/25   case s21   policy forms: HO-0309
==============================================================================
ADJUSTER NOTES:
Claim # 2024-70488, [CLAIMANT_NAME], HO-0309 ed. 05-24. Insured is a self-employed accountant working from a converted front room with a sign at the gate; clients visit about three times a week. On 6 Nov 2024 a client slipped on the office step and has claimed for a broken wrist.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0309
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 15, 2024
Title: Business Pursuits Exclusion — In-Home Office Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement covers how the policy responds to business carried on at or
from the described dwelling — home offices, in-home businesses, remote work,
and care-giving operations run from the premises.

CLAUSE BP-1 — BUSINESS PURSUITS EXCLUSION
We do not cover bodily injury or property damage arising out of or in connection
with a business engaged in by an insured. This exclusion applies regardless
of whether the business activity occurs at the described premises.

CLAUSE BP-2 — IN-HOME OFFICE EXCEPTION (LIMITED)
Notwithstanding CLAUSE BP-1, if the insured's use of a portion of the
described dwelling as an office is solely incidental to a primary occupation
conducted elsewhere, we will cover:
  (a) Up to $2,500 in business equipment located at the dwelling;
  (b) Liability arising from a single, non-client business invitee visit
      per calendar week.
This exception does NOT apply if the dwelling is the primary place of business.

CLAUSE BP-3 — HOME DAY CARE EXCLUSION
Coverage is excluded for any bodily injury or property damage arising from
a home day care, foster care, or after-school care operation conducted
at the described premises, regardless of whether compensation is received.

CLAUSE BP-4 — SIGNAGE AND CLIENT TRAFFIC
The CLAUSE BP-2 exception is void for any policy period in which the dwelling
displays commercial signage or receives client foot traffic more often than
the single weekly visit allowed above.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0309 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-19 | Business pursuits liability                | BI/PD from any business activity; see CLAUSE BP-1                 |
|      |                                            | Business pursuits exclusion E-19 IS present in HO-0309 ed. 05-24  |
| E-36 | Home day care and foster care liability    | Any paid care-giving operation run at the described premises       |
| E-37 | Business inventory and stock               | Merchandise or stock-in-trade held for sale; excluded under Cov C  |
| E-38 | Professional liability / errors & omissions| Claims arising from professional services rendered from home       |
| E-39 | Employer's liability — domestic workers    | Household employee claims for work-related injury                  |

SECTION III — BUSINESS EQUIPMENT SUBLIMIT
The $2,500 sublimit under CLAUSE BP-2 is per occurrence and per policy year.
Equipment worth more than $2,500 needs a separate Inland Marine floater.
Electronic data and software fall outside this sublimit entirely.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 15, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0309 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-70488  

DATE OF LOSS: 06 Nov 2024  

POLICY FORMS: HO-0309 (Business Pursuits Exclusion — In‑Home Office Endorsement) attached to the Homeowners Policy — Special Form  

LOSS SUMMARY: The insured, a self‑employed accountant, operates a home office in a converted front room. A client visiting the office slipped on the office step and suffered a broken wrist.  

DEDUCTIBLE: Undetermined – the deductible schedule is provided in HO‑0305 § III, which requires the dwelling’s insured value to calculate the amount (e.g., $5,000 minimum or 2 % of Cov‑A) [SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III]. The insured value is not supplied in the adjuster notes.  

COVERAGE POSITION: Not covered. The liability claim is excluded under the Business Pursuits Exclusion (BP‑1) [SOURCE: HO-0309_sa_chunk_003 | HO-0309 | CLAUSE-BP-1]. The In‑Home Office Exception (BP‑2) does not apply because the dwelling is the primary place of business and the incident involved a client (a business invitee) visiting more than the single, non‑client invitee per week allowed by the exception [SOURCE: HO-0309_sa_chunk_004 | HO-0309 | CLAUSE-BP-2].  

EXCLUSIONS APPLIED: Business Pursuits Exclusion (BP‑1) – excludes bodily injury arising out of the insured’s business activities.  

OPEN ITEMS:  
- Confirmation of the dwelling’s insured value to determine the applicable deductible.  
- Verification of any additional endorsements or separate liability policies that might provide coverage.  
- Documentation of the client’s status (e.g., whether considered a “non‑client business invitee”) for completeness, though coverage is already excluded.
==============================================================================
```

```
==============================================================================
SUMMARY 3/25   case s05   policy forms: HO-0304
==============================================================================
ADJUSTER NOTES:
CLM 2024-33058, [CLAIMANT_NAME], HO-0304 03-24, $1,000 ded. Dishwasher overflowed on 2 May 2024 and flooded the kitchen floor. Unit is 17 years old per the serial plate; insured confirms it was never serviced. Floor and lower cabinets damaged, estimate $6,200.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-33058  
DATE OF LOSS: 2 May 2024  
POLICY FORMS: HO-0304 (03‑24 endorsement)  

LOSS SUMMARY: The insured’s dishwasher overflowed, flooding the kitchen floor, lower cabinets, and surrounding flooring. The estimated repair cost for the damaged floor and cabinets is $6,200.  

DEDUCTIBLE: The only deductible language provided in the endorsement materials pertains to the Named Storm deductible (minimum $5,000 or 2 % of Coverage A) [SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III] and does not address a water‑damage loss from a dishwasher overflow. Consequently, the applicable deductible for this loss is undetermined from the supplied policy language.  

COVERAGE POSITION: The endorsement excerpts do not contain a provision that expressly covers water damage caused by a malfunctioning appliance such as a dishwasher. The only water‑related endorsement (HO‑0304) modifies coverage for water supply line damage [SOURCE: HO-0304_sa_chunk_009 | HO-0304 | SECTION‑IV] and does not extend to appliance overflows. Therefore, coverage for this loss is undetermined based on the provided policy wording.  

EXCLUSIONS APPLIED: No specific exclusion language relevant to this loss is present in the supplied endorsement excerpts.  

OPEN ITEMS:  
- Confirmation of the applicable deductible (policy language for non‑storm water damage).  
- Verification of any additional coverage provisions or exclusions not included in the provided excerpts that may apply to appliance‑originated water damage.  
- Obtain any required documentation (e.g., proof of timely reporting, contractor estimates) if coverage is later confirmed.
==============================================================================
```

```
==============================================================================
SUMMARY 4/25   case s03   policy forms: HO-0309
==============================================================================
ADJUSTER NOTES:
CLM-2024-52210. Insured [CLAIMANT_NAME], HO-0309 ed. 05-24. On 19 Aug 2024 a neighbour's four-year-old broke an arm falling off a climbing frame in the insured's back yard. Insured looks after three neighbours' children on weekdays; says she takes no money for it, the parents 'help out with groceries'. Parents have sent a letter of claim for medical costs. Liability claim only, no property damage.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0309
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 15, 2024
Title: Business Pursuits Exclusion — In-Home Office Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement covers how the policy responds to business carried on at or
from the described dwelling — home offices, in-home businesses, remote work,
and care-giving operations run from the premises.

CLAUSE BP-1 — BUSINESS PURSUITS EXCLUSION
We do not cover bodily injury or property damage arising out of or in connection
with a business engaged in by an insured. This exclusion applies regardless
of whether the business activity occurs at the described premises.

CLAUSE BP-2 — IN-HOME OFFICE EXCEPTION (LIMITED)
Notwithstanding CLAUSE BP-1, if the insured's use of a portion of the
described dwelling as an office is solely incidental to a primary occupation
conducted elsewhere, we will cover:
  (a) Up to $2,500 in business equipment located at the dwelling;
  (b) Liability arising from a single, non-client business invitee visit
      per calendar week.
This exception does NOT apply if the dwelling is the primary place of business.

CLAUSE BP-3 — HOME DAY CARE EXCLUSION
Coverage is excluded for any bodily injury or property damage arising from
a home day care, foster care, or after-school care operation conducted
at the described premises, regardless of whether compensation is received.

CLAUSE BP-4 — SIGNAGE AND CLIENT TRAFFIC
The CLAUSE BP-2 exception is void for any policy period in which the dwelling
displays commercial signage or receives client foot traffic more often than
the single weekly visit allowed above.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0309 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-19 | Business pursuits liability                | BI/PD from any business activity; see CLAUSE BP-1                 |
|      |                                            | Business pursuits exclusion E-19 IS present in HO-0309 ed. 05-24  |
| E-36 | Home day care and foster care liability    | Any paid care-giving operation run at the described premises       |
| E-37 | Business inventory and stock               | Merchandise or stock-in-trade held for sale; excluded under Cov C  |
| E-38 | Professional liability / errors & omissions| Claims arising from professional services rendered from home       |
| E-39 | Employer's liability — domestic workers    | Household employee claims for work-related injury                  |

SECTION III — BUSINESS EQUIPMENT SUBLIMIT
The $2,500 sublimit under CLAUSE BP-2 is per occurrence and per policy year.
Equipment worth more than $2,500 needs a separate Inland Marine floater.
Electronic data and software fall outside this sublimit entirely.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 15, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0309 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-52210  
DATE OF LOSS: 19 Aug 2024  
POLICY FORMS: HO-0309 (ed. 05‑24)  

LOSS SUMMARY: On 19 Aug 2024 a neighbor’s four‑year‑old child fell from a climbing frame in the insured’s backyard and sustained a broken arm. The insured regularly looks after three neighboring children on weekdays without receiving monetary compensation; the parents have submitted a claim for the child’s medical expenses. The claim is for liability only; no property damage is involved.  

DEDUCTIBLE: Undetermined – the provided endorsement excerpts do not contain any deductible language applicable to liability coverage under HO‑0309.  

COVERAGE POSITION: Excluded. The injury arose from a home day‑care‑type activity conducted at the insured’s residence, which is expressly excluded from coverage.  
[ SOURCE: HO-0309_sa_chunk_005 | HO-0309 | CLAUSE-BP-3 ]  

EXCLUSIONS APPLIED: Home Day Care Exclusion – bodily injury arising from a home day‑care, foster‑care, or after‑school‑care operation at the described premises is not covered.  
[ SOURCE: HO-0309_sa_chunk_005 | HO-0309 | CLAUSE-BP-3 ]  

OPEN ITEMS:  
- Obtain documentation from the parents confirming the nature of the care arrangement (e.g., informal babysitting vs. formal day‑care).  
- Request medical bills and any related expense statements for the child’s treatment.  
- Verify that no other policy forms or endorsements (not provided) could modify the exclusion.
==============================================================================
```

```
==============================================================================
SUMMARY 5/25   case s18   policy forms: HO-0305, HO-0306
==============================================================================
ADJUSTER NOTES:
Claim 2024-61622. Insured [CLAIMANT_NAME], HO-0305 ed. 03-24 and HO-0306 ed. 04-24, Coverage A $500,000. Named storm Helene flooded the detached garage through a torn roof on 27 Sept 2024. Destroyed: $6,500 of candle stock the insured sells online, plus $3,200 of garage roof damage.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0305
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 15, 2024
Title: Increased Deductible for Named Storm Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement sets a separate, higher deductible that applies only to loss
caused by a Named Storm as defined below. Every other covered peril continues
to be settled under the standard policy deductible.

CLAUSE NS-1 — NAMED STORM DEFINITION
A "Named Storm" means a tropical cyclone, hurricane, or tropical storm that has
been assigned a name by the National Hurricane Center (NHC) or the equivalent
national meteorological authority at any point during its lifecycle, regardless
of whether the storm bore a name at the time it caused loss to the described
premises.

CLAUSE NS-2 — NAMED STORM DEDUCTIBLE
When a Named Storm causes or contributes to a covered loss, the Named Storm
Deductible is $5,000 or 2% of the Coverage A limit, whichever is greater.
This deductible applies per occurrence, not per storm season.

CLAUSE NS-3 — STACKING PROHIBITION
The Named Storm Deductible under this endorsement replaces — and does not stack
with — any all-peril deductible stated on the declarations page. The higher
of the two deductibles applies.

CLAUSE NS-4 — TRIGGER WINDOW
The Named Storm Deductible attaches from the time the NHC issues a watch or
warning for the county of the described premises until 72 hours after the
final advisory for that storm is published.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0305 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-20 | Temporary repairs not documented           | Emergency repairs claimed without photographs or invoices          |
| E-21 | Losses below Named Storm deductible        | Total damage under the Named Storm deductible is not payable       |
| E-22 | Coastal storm surge classified as flood    | Surge loss falls to NFIP and is not covered by this form           |
| E-23 | Pre-existing wind damage                   | Damage already present before the Named Storm made landfall        |
| E-24 | Business property in dwelling              | Commercial inventory or equipment kept on the premises             |

SECTION III — DEDUCTIBLE SCHEDULE
Policy Year 2024 Named Storm Deductible: $5,000 minimum or 2% of Cov-A.
For a dwelling insured at $300,000: deductible = $6,000.
For a dwelling insured at $200,000: deductible = $5,000 (floor applies).

SECTION IV — EFFECTIVE DATE
This endorsement is effective March 15, 2024.
Premium adjustment: $0.00 (deductible shift, no additional premium).

END OF ENDORSEMENT HO-0305 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0306
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 1, 2024
Title: Mold, Fungi, and Wet Rot Exclusion Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement settles how the policy treats mold, fungi, wet rot, dry rot,
and bacteria, whether those conditions follow a covered water loss or arise on
their own. It narrows the base wording rather than adding to it.

CLAUSE MF-1 — MOLD AND FUNGI EXCLUSION (GENERAL)
We do not cover loss caused directly or indirectly by mold, fungi, wet rot,
dry rot, or bacteria. This exclusion applies regardless of whether the mold
or fungi results from a covered or uncovered water event.

CLAUSE MF-2 — REMEDIATION SUBLIMIT EXCEPTION
Notwithstanding CLAUSE MF-1, if mold is a direct result of a covered sudden
and accidental water discharge event (as defined in form HO-0304 ed. 03-24,
CLAUSE WD-1), we will pay up to $10,000 for mold remediation costs, provided:
  (a) The water event is reported within 72 hours of discovery, and
  (b) A licensed remediation contractor provides a written estimate.

CLAUSE MF-3 — TESTING EXCLUSION
We do not cover the cost of air quality testing, mold sampling, or laboratory
analysis, even if the underlying remediation is covered under CLAUSE MF-2.

CLAUSE MF-4 — SUBLIMIT IS NOT ADDITIONAL INSURANCE
The $10,000 remediation sublimit is part of, and not in addition to, the
Coverage A limit. Payment under MF-2 reduces the amount available for the
underlying water loss.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0306 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-22 | Mold damage — general                      | All mold-related losses UNLESS remediation sublimit applies        |
| E-23 | Fungi and wet rot losses                   | Wet rot, dry rot, or fungi in any form, whatever the water source  |
| E-24 | Bacteria contamination                     | Loss attributable to bacterial growth or contamination             |
| E-25 | Mold testing and air sampling costs        | Lab, air-quality, and surface sampling charges are not payable     |
| E-26 | Pre-existing mold at time of policy issue  | Mold present anywhere in the dwelling before policy inception      |
| E-27 | Mold from HVAC condensation (chronic)      | Condensation mold where the HVAC system is 3+ years unserviced     |

SECTION III — CONDITIONS
Nothing in this endorsement widens coverage beyond what it states outright.
Where this endorsement and the base policy disagree on a mold or fungi loss,
this endorsement governs.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement, no additional premium).

END OF ENDORSEMENT HO-0306 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-61622  
DATE OF LOSS: 27 September 2024  
POLICY FORMS: HO-0305 ed. 03-24 (Homeowners – Increased Deductible for Named Storm Endorsement); HO-0306 ed. 04-24 (referenced in adjuster notes) – Coverage A limit $500,000.  

LOSS SUMMARY: The named storm “Helene” caused a torn roof on the insured’s detached garage, resulting in roof damage estimated at $3,200. In addition, $6,500 of candle inventory stored in the garage was destroyed.  

DEDUCTIBLE: The Named Storm deductible is the greater of $5,000 or 2 % of the Coverage A limit. With a $500,000 limit, 2 % equals $10,000, which exceeds the $5,000 floor; therefore the applicable deductible is $10,000 per occurrence. [SOURCE: HO-0305_sa_chunk_004 | HO-0305 | CLAUSE-NS-2]  

COVERAGE POSITION: The total loss ($3,200 roof damage + $6,500 candle stock = $9,700) is below the $10,000 Named Storm deductible, so no payment is made for the roof damage under the deductible provision. The candle stock is classified as business property kept in the dwelling, which is expressly excluded. Consequently, the claim is not payable.  

EXCLUSIONS APPLIED:  
- E‑21 – Losses below the Named Storm deductible are not payable. [SOURCE: HO-0305_sa_chunk_008 | HO-0305 | EXCLUSION-TABLE]  
- E‑24 – Business property located in the dwelling is excluded. [SOURCE: HO-0305_sa_chunk_008 | HO-0305 | EXCLUSION-TABLE]  

OPEN ITEMS:  
1. Confirmation that the candle inventory qualifies as “business property” under exclusion E‑24.  
2. Verification of any documentation (photos, invoices) for the roof damage to support the loss amount.  
3. Determination whether any portion of the loss might be covered under a separate business property endorsement (not provided in the current endorsement set).
==============================================================================
```

```
==============================================================================
SUMMARY 6/25   case s07   policy forms: HO-0308
==============================================================================
ADJUSTER NOTES:
CLM-2024-58830, [CLAIMANT_NAME], HO-0308 ed. 05-24, $1,000 deductible. Ceiling in the rear bedroom sagged and cracked, discovered 15 July 2024. Our structural engineer's report: roof trusses were undersized at construction; foundation level, no soil movement, earth movement did NOT contribute. Insured's builder blames a storm. Need to know where coverage stands.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0308
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 1, 2024
Title: Earth Movement Exclusion — Broadened Definition Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement widens the earth movement exclusion in the base homeowners
policy and removes the ambiguity that has driven disputed determinations on
sinkholes, soil subsidence, and expansive soil claims.

CLAUSE EM-1 — EARTH MOVEMENT DEFINED (BROADENED)
For purposes of this endorsement, "earth movement" means any movement,
shifting, rising, sinking, settling, or destabilizing of the earth or soil,
including but not limited to:
  (a) Earthquake, including tremors, aftershocks, and volcanic eruption;
  (b) Landslide, mudslide, or debris flow;
  (c) Sinkhole formation or collapse;
  (d) Soil subsidence or expansive soil events;
  (e) Man-made earth movement, including mining-induced subsidence.

CLAUSE EM-2 — CONCURRENT CAUSATION RULE
If earth movement and a covered peril act concurrently or in sequence to
produce a loss, the entire loss is excluded under this endorsement.
Coverage does not attach to any portion of the loss attributable to
the covered peril when earth movement is also a contributing cause.

CLAUSE EM-3 — ENSUING FIRE EXCEPTION
Notwithstanding CLAUSE EM-1 and EM-2, if earth movement causes a fire,
coverage for the ensuing fire damage is not excluded by this endorsement.

CLAUSE EM-4 — ENGINEERING REPORT
Where the Company obtains a geotechnical or structural engineering report on
a claimed loss, that report is the controlling evidence of whether earth
movement contributed to the damage.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0308 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-31 | Earth movement — all forms                 | Earthquake, landslide, mudslide, sinkhole, subsidence; all forms   |
|      |                                            | of earth movement as defined in CLAUSE EM-1 are excluded.          |
|      |                                            | Concurrent cause rule applies (CLAUSE EM-2).                       |
| E-32 | Man-made earth movement                    | Mining subsidence, excavation-induced movement, compaction failure |
| E-33 | Sinkhole collapse damage                   | Structural damage from sinkhole formation or sudden collapse       |
| E-34 | Expansive soil and shrinkage               | Foundation cracking from soil expansion, shrinkage, or settlement  |
| E-35 | Mudslide and debris flow                   | Flowing earth, mud, or debris whatever set it in motion            |

SECTION III — ENSUING LOSS EXCEPTION NOTE
Ensuing fire under CLAUSE EM-3 is the only exception to this exclusion.
Water damage that follows from pipes ruptured by earth movement stays
excluded under E-31 through the concurrent cause rule in CLAUSE EM-2.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0308 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-58830  

DATE OF LOSS: 15 July 2024 (date loss discovered)  

POLICY FORMS: HO-0308 (ed. 05‑24)  

LOSS SUMMARY: The rear‑bedroom ceiling sagged and cracked and was discovered on 15 July 2024. The insurer’s structural engineer reports that roof trusses were undersized at construction and that there was no soil or earth movement contributing to the damage. The insured’s builder attributes the loss to a storm, but no engineering evidence links the storm to the damage.  

DEDUCTIBLE: The policy’s Named Storm deductible is the greater of $5,000 or 2 % of the Coverage A limit, applied per occurrence [ SOURCE: HO-0305_sa_chunk_004 | HO-0305 | CLAUSE-NS-2 ]. The deductible schedule also sets a $5,000 minimum (or 2 % of Coverage A) for the 2024 policy year [ SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III ]. The adjuster’s note of a “$1,000 deductible” is not reflected in the provided policy wording.  

COVERAGE POSITION: Undetermined – the policy does not contain a specific coverage provision in the supplied excerpts that confirms or denies coverage for ceiling damage alleged to be caused by a storm. Because the engineering report finds no earth movement and does not establish storm causation, there is insufficient information to apply coverage.  

EXCLUSIONS APPLIED:  
- **E‑21 – Losses below Named Storm deductible** – If the total damage amount is less than the applicable $5,000 (or 2 % of Coverage A) deductible, the loss would be excluded [ SOURCE: HO-0305_sa_chunk_008 | HO-0305 | EXCLUSION-TABLE ].  

No other exclusions (e.g., E‑23 pre‑existing wind damage) are directly triggered by the facts provided.  

OPEN ITEMS:  
1. Determine the actual loss amount to assess whether it exceeds the Named Storm deductible.  
2. Obtain the Coverage A limit to calculate the 2 % deductible threshold.  
3. Gather additional evidence (e.g., meteorological data, damage photos) to establish whether the storm caused the ceiling damage.  
4. Clarify the source of the “$1,000 deductible” referenced in the adjuster’s note and reconcile it with the policy’s deductible provisions.
==============================================================================
```

```
==============================================================================
SUMMARY 7/25   case s24   policy forms: HO-0305
==============================================================================
ADJUSTER NOTES:
clm 2024-61301, HO-0305, Cov A $260k. Helene 26/09/2024. Insured put up tarp + plywood himself, wants $3,100 back. No photos, no receipts. No other damage claimed.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0305
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 15, 2024
Title: Increased Deductible for Named Storm Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement sets a separate, higher deductible that applies only to loss
caused by a Named Storm as defined below. Every other covered peril continues
to be settled under the standard policy deductible.

CLAUSE NS-1 — NAMED STORM DEFINITION
A "Named Storm" means a tropical cyclone, hurricane, or tropical storm that has
been assigned a name by the National Hurricane Center (NHC) or the equivalent
national meteorological authority at any point during its lifecycle, regardless
of whether the storm bore a name at the time it caused loss to the described
premises.

CLAUSE NS-2 — NAMED STORM DEDUCTIBLE
When a Named Storm causes or contributes to a covered loss, the Named Storm
Deductible is $5,000 or 2% of the Coverage A limit, whichever is greater.
This deductible applies per occurrence, not per storm season.

CLAUSE NS-3 — STACKING PROHIBITION
The Named Storm Deductible under this endorsement replaces — and does not stack
with — any all-peril deductible stated on the declarations page. The higher
of the two deductibles applies.

CLAUSE NS-4 — TRIGGER WINDOW
The Named Storm Deductible attaches from the time the NHC issues a watch or
warning for the county of the described premises until 72 hours after the
final advisory for that storm is published.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0305 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-20 | Temporary repairs not documented           | Emergency repairs claimed without photographs or invoices          |
| E-21 | Losses below Named Storm deductible        | Total damage under the Named Storm deductible is not payable       |
| E-22 | Coastal storm surge classified as flood    | Surge loss falls to NFIP and is not covered by this form           |
| E-23 | Pre-existing wind damage                   | Damage already present before the Named Storm made landfall        |
| E-24 | Business property in dwelling              | Commercial inventory or equipment kept on the premises             |

SECTION III — DEDUCTIBLE SCHEDULE
Policy Year 2024 Named Storm Deductible: $5,000 minimum or 2% of Cov-A.
For a dwelling insured at $300,000: deductible = $6,000.
For a dwelling insured at $200,000: deductible = $5,000 (floor applies).

SECTION IV — EFFECTIVE DATE
This endorsement is effective March 15, 2024.
Premium adjustment: $0.00 (deductible shift, no additional premium).

END OF ENDORSEMENT HO-0305 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-61301  
DATE OF LOSS: 26/09/2024 (Helene)  
POLICY FORMS: HO-0305 (Increased Deductible for Named Storm Endorsement)  

LOSS SUMMARY: The insured installed a tarp and plywood as temporary repairs after the named storm. He is requesting reimbursement of $3,100 but provided no photographs or receipts to document the work. No other damage has been claimed.  

DEDUCTIBLE: The Named Storm deductible is the greater of $5,000 or 2 % of Coverage A. With Coverage A of $260,000, 2 % equals $5,200, which exceeds the $5,000 floor; therefore the deductible is $5,200. [SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III]  

COVERAGE POSITION: The claim is not payable. The requested amount ($3,100) is below the applicable deductible of $5,200, and the temporary repairs lack the required documentation (photos or invoices). Both conditions trigger exclusions that preclude payment.  

EXCLUSIONS APPLIED:  
- E-20 – Temporary repairs not documented (no photographs or invoices). [SOURCE: HO-0305_sa_chunk_008 | HO-0305 | EXCLUSION-TABLE]  
- E-21 – Losses below Named Storm deductible (claimed amount under deductible). [SOURCE: HO-0305_sa_chunk_008 | HO-0305 | EXCLUSION-TABLE]  

OPEN ITEMS: None – the claim is fully excluded based on the provided information.
==============================================================================
```

```
==============================================================================
SUMMARY 8/25   case s20   policy forms: HO-0304
==============================================================================
ADJUSTER NOTES:
CLM-2024-30016, [CLAIMANT_NAME], HO-0304 ed. 03-24, deductible $1,000. Rental-between-tenants house was empty from February. Heating turned off and main water left on. Pipes froze and split on 20 March 2024; found a week later by the letting agent. Damage estimate $16,200.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-30016  

DATE OF LOSS: 20 March 2024  

POLICY FORMS: HO-0304 (Water Damage Limitations and Supply Line Coverage Endorsement) – 03/24 edition; deductible schedule referenced from HO-0305 – 03/24 edition.  

LOSS SUMMARY: The rental property was vacant from February 2024, the heating system was turned off and the main water supply remained on. On 20 March 2024 the interior water pipes froze, split, and caused water damage discovered a week later; the estimated loss is $16,200.  

DEDUCTIBLE: Adjuster’s file notes a $1,000 deductible, however the policy’s deductible schedule sets a minimum deductible of $5,000 (or 2 % of Coverage‑A) for the 2024 policy year【SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III】.  

COVERAGE POSITION: The loss is excluded under the “Unoccupied dwelling freeze loss” exclusion (Code E‑10). The facts—heating turned off, water not shut off, and the dwelling was unoccupied—match the exclusion’s conditions【SOURCE: HO-0304_sa_chunk_007 | HO-0304 | EXCLUSION-TABLE】. Consequently, coverage under the HO‑0304 endorsement is denied.  

EXCLUSIONS APPLIED:  
- E‑10 – Unoccupied dwelling freeze loss (applies).  

COVERAGE THAT DOES NOT APPLY: Although the endorsement expressly states that a “Burst supply line” is covered (E‑17)【SOURCE: HO-0304_sa_chunk_007 | HO-0304 | EXCLUSION-TABLE】, the loss resulted from freeze‑induced pipe rupture, not a sudden burst, so the E‑17 provision is not triggered.  

OPEN ITEMS:  
1. Confirmation of the applicable deductible amount (adjuster notes $1,000 vs. policy minimum $5,000).  
2. Verification of any additional documentation required to substantiate the unoccupied status and heating shutdown (e.g., tenant move‑out notice, utility records).  
3. Final loss verification and any potential salvage or mitigation costs.
==============================================================================
```

```
==============================================================================
SUMMARY 9/25   case s16   policy forms: HO-0307, HO-0308
==============================================================================
ADJUSTER NOTES:
claim no. 2024-67003, [CLAIMANT_NAME], HO-0307 ed. 04-24 and HO-0308 ed. 05-24, $250 deductible. On 22 July 2024 customs officers seized the insured's scheduled Rolex (schedule value $14,500, appraisal 2022) at the airport; seizure order attached. Watch not returned.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0307
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 15, 2024
Title: Scheduled Personal Property Floater Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement extends coverage to personal property that is individually
listed and appraised on the Declarations Page, and lifts the Coverage C
sublimits that would otherwise cap those categories.

CLAUSE SP-1 — SCHEDULED ITEMS
Items specifically scheduled on the Declarations Page Schedule of Personal
Property are covered for their appraised replacement value, without application
of the standard Coverage C sublimits for jewelry, watches, furs, silverware,
firearms, or musical instruments.

CLAUSE SP-2 — WORLDWIDE COVERAGE
Scheduled items receive coverage on a worldwide basis for all risks of direct
physical loss unless specifically excluded herein or in the base policy.

CLAUSE SP-3 — PAIR AND SET CLAUSE
In the event of loss to one item of a pair or set, we pay only the difference
between the appraised value of the pair or set and the fair market value of
the undamaged item(s).

CLAUSE SP-4 — NEWLY ACQUIRED ITEMS
An item newly acquired in a scheduled category is covered automatically for
30 days from the date of purchase, up to 25% of the total schedule value,
after which it must be added to the schedule by written request.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0307 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-28 | Mysterious disappearance — unscheduled     | Unlisted items carry no mysterious disappearance coverage          |
| E-29 | Gradual deterioration of scheduled items   | Wear, tear, inherent vice, or gradual deterioration                |
| E-30 | War and nuclear peril                      | Loss caused by war, nuclear reaction, or radioactive contamination |
| E-31 | Earth movement — all forms                 | Loss caused by earthquake, landslide, subsidence, or earth sinking |
|      |                                            | Earth movement exclusion applies to SCHEDULED items under HO-0307  |
| E-32 | Government action / confiscation           | Seizure or destruction ordered by a governmental authority         |

SECTION III — APPRAISAL REQUIREMENT
Every item scheduled here must have a current appraisal on file with the
Company, dated within 36 months. An item whose appraisal has lapsed falls back
to the Coverage C sublimits until a current appraisal is supplied.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 15, 2024.
Premium adjustment: Based on schedule value; see Declarations Page.

END OF ENDORSEMENT HO-0307 ed. 04-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0308
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 1, 2024
Title: Earth Movement Exclusion — Broadened Definition Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement widens the earth movement exclusion in the base homeowners
policy and removes the ambiguity that has driven disputed determinations on
sinkholes, soil subsidence, and expansive soil claims.

CLAUSE EM-1 — EARTH MOVEMENT DEFINED (BROADENED)
For purposes of this endorsement, "earth movement" means any movement,
shifting, rising, sinking, settling, or destabilizing of the earth or soil,
including but not limited to:
  (a) Earthquake, including tremors, aftershocks, and volcanic eruption;
  (b) Landslide, mudslide, or debris flow;
  (c) Sinkhole formation or collapse;
  (d) Soil subsidence or expansive soil events;
  (e) Man-made earth movement, including mining-induced subsidence.

CLAUSE EM-2 — CONCURRENT CAUSATION RULE
If earth movement and a covered peril act concurrently or in sequence to
produce a loss, the entire loss is excluded under this endorsement.
Coverage does not attach to any portion of the loss attributable to
the covered peril when earth movement is also a contributing cause.

CLAUSE EM-3 — ENSUING FIRE EXCEPTION
Notwithstanding CLAUSE EM-1 and EM-2, if earth movement causes a fire,
coverage for the ensuing fire damage is not excluded by this endorsement.

CLAUSE EM-4 — ENGINEERING REPORT
Where the Company obtains a geotechnical or structural engineering report on
a claimed loss, that report is the controlling evidence of whether earth
movement contributed to the damage.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0308 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-31 | Earth movement — all forms                 | Earthquake, landslide, mudslide, sinkhole, subsidence; all forms   |
|      |                                            | of earth movement as defined in CLAUSE EM-1 are excluded.          |
|      |                                            | Concurrent cause rule applies (CLAUSE EM-2).                       |
| E-32 | Man-made earth movement                    | Mining subsidence, excavation-induced movement, compaction failure |
| E-33 | Sinkhole collapse damage                   | Structural damage from sinkhole formation or sudden collapse       |
| E-34 | Expansive soil and shrinkage               | Foundation cracking from soil expansion, shrinkage, or settlement  |
| E-35 | Mudslide and debris flow                   | Flowing earth, mud, or debris whatever set it in motion            |

SECTION III — ENSUING LOSS EXCEPTION NOTE
Ensuing fire under CLAUSE EM-3 is the only exception to this exclusion.
Water damage that follows from pipes ruptured by earth movement stays
excluded under E-31 through the concurrent cause rule in CLAUSE EM-2.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0308 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-67003  
DATE OF LOSS: 22 July 2024  
POLICY FORMS: HO-0307 ed. 04-24 (Scheduled Personal Property Floater Endorsement); HO-0308 ed. 05-24 (referenced in adjuster notes)  
LOSS SUMMARY: On 22 July 2024, customs officers seized the insured’s scheduled Rolex watch (schedule value $14,500, appraisal dated 2022) at the airport. A seizure order was issued and the watch has not been returned to the insured.  
DEDUCTIBLE: $250 (as noted by the adjuster)  
COVERAGE POSITION: Undetermined – the provided endorsement excerpts contain only effective dates and a preamble indicating the endorsement modifies the Homeowners Special Form, but they do not include the specific coverage language that confirms whether scheduled personal property (such as a Rolex watch) is covered for loss due to seizure by customs. Without the relevant coverage clause, a coverage determination cannot be made.  
EXCLUSIONS APPLIED: Undetermined – no exclusion language regarding seizure by customs or government authority is present in the supplied endorsement excerpts. Consequently, it cannot be concluded whether an exclusion applies to this loss.  
OPEN ITEMS:  
- Full policy language for HO-0307 (especially the coverage provisions for scheduled personal property).  
- Any applicable exclusion language (e.g., government seizure, customs).  
- Proof of ownership/appraisal documentation for the Rolex.  
- Copy of the customs seizure order and any related correspondence.  
- Confirmation of the $250 deductible applicability under the policy’s deductible schedule.
==============================================================================
```

```
==============================================================================
SUMMARY 10/25   case s23   policy forms: HO-0307
==============================================================================
ADJUSTER NOTES:
CLM-2024-66950. HO-0307. $250 ded. Ring gone, 12 Aug 2024. Insured doesn't know where or how. Not on the schedule.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0307
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 15, 2024
Title: Scheduled Personal Property Floater Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement extends coverage to personal property that is individually
listed and appraised on the Declarations Page, and lifts the Coverage C
sublimits that would otherwise cap those categories.

CLAUSE SP-1 — SCHEDULED ITEMS
Items specifically scheduled on the Declarations Page Schedule of Personal
Property are covered for their appraised replacement value, without application
of the standard Coverage C sublimits for jewelry, watches, furs, silverware,
firearms, or musical instruments.

CLAUSE SP-2 — WORLDWIDE COVERAGE
Scheduled items receive coverage on a worldwide basis for all risks of direct
physical loss unless specifically excluded herein or in the base policy.

CLAUSE SP-3 — PAIR AND SET CLAUSE
In the event of loss to one item of a pair or set, we pay only the difference
between the appraised value of the pair or set and the fair market value of
the undamaged item(s).

CLAUSE SP-4 — NEWLY ACQUIRED ITEMS
An item newly acquired in a scheduled category is covered automatically for
30 days from the date of purchase, up to 25% of the total schedule value,
after which it must be added to the schedule by written request.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0307 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-28 | Mysterious disappearance — unscheduled     | Unlisted items carry no mysterious disappearance coverage          |
| E-29 | Gradual deterioration of scheduled items   | Wear, tear, inherent vice, or gradual deterioration                |
| E-30 | War and nuclear peril                      | Loss caused by war, nuclear reaction, or radioactive contamination |
| E-31 | Earth movement — all forms                 | Loss caused by earthquake, landslide, subsidence, or earth sinking |
|      |                                            | Earth movement exclusion applies to SCHEDULED items under HO-0307  |
| E-32 | Government action / confiscation           | Seizure or destruction ordered by a governmental authority         |

SECTION III — APPRAISAL REQUIREMENT
Every item scheduled here must have a current appraisal on file with the
Company, dated within 36 months. An item whose appraisal has lapsed falls back
to the Coverage C sublimits until a current appraisal is supplied.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 15, 2024.
Premium adjustment: Based on schedule value; see Declarations Page.

END OF ENDORSEMENT HO-0307 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-66950  
DATE OF LOSS: 12 Aug 2024  
POLICY FORMS: HO-0307 (Scheduled Personal Property Floater Endorsement); HO-0305 (Homeowners Policy – Special Form)  

LOSS SUMMARY: The insured reported that a ring was missing as of 12 August 2024. The insured does not know how or where the loss occurred. The ring was not listed on the Schedule of Personal Property attached to the policy.  

DEDUCTIBLE: $250 deductible noted in the adjuster’s file. The policy’s deductible schedule for named storm losses is $5,000 minimum or 2 % of Coverage A (see HO‑0305 § III) [SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III]. The $250 figure is not addressed in the endorsement language and therefore remains an adjuster‑provided fact.  

COVERAGE POSITION: The ring is **not covered** under the Scheduled Personal Property Floater endorsement because coverage is limited to items specifically scheduled on the Declarations Page Schedule of Personal Property. The ring was not on that schedule.  
[ SOURCE: HO-0307_sa_chunk_003 | HO-0307 | CLAUSE-SP-1 ]  

EXCLUSIONS APPLIED: Items not specifically scheduled are excluded from coverage under the endorsement.  
[ SOURCE: HO-0307_sa_chunk_003 | HO-0307 | CLAUSE-SP-1 ]  

OPEN ITEMS:  
- Proof of ownership/appraisal for the missing ring.  
- Confirmation of whether the ring was ever added to the schedule after the policy effective date.  
- Clarification of the applicable deductible (whether the $250 adjuster‑noted amount or the policy‑specified storm deductible applies to this loss).
==============================================================================
```

```
==============================================================================
SUMMARY 11/25   case s19   policy forms: HO-0307, HO-0308
==============================================================================
ADJUSTER NOTES:
CLM-2024-58112, [CLAIMANT_NAME], HO-0307 04-24 and HO-0308 05-24, ded $1,000. Sinkhole opened under the west corner of the house on 4 June 2024; foundation cracked, living room floor dropped. The insured's scheduled Steinway piano (schedule value $42,000, appraisal 2024) fell through the floor and was destroyed.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0307
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 15, 2024
Title: Scheduled Personal Property Floater Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement extends coverage to personal property that is individually
listed and appraised on the Declarations Page, and lifts the Coverage C
sublimits that would otherwise cap those categories.

CLAUSE SP-1 — SCHEDULED ITEMS
Items specifically scheduled on the Declarations Page Schedule of Personal
Property are covered for their appraised replacement value, without application
of the standard Coverage C sublimits for jewelry, watches, furs, silverware,
firearms, or musical instruments.

CLAUSE SP-2 — WORLDWIDE COVERAGE
Scheduled items receive coverage on a worldwide basis for all risks of direct
physical loss unless specifically excluded herein or in the base policy.

CLAUSE SP-3 — PAIR AND SET CLAUSE
In the event of loss to one item of a pair or set, we pay only the difference
between the appraised value of the pair or set and the fair market value of
the undamaged item(s).

CLAUSE SP-4 — NEWLY ACQUIRED ITEMS
An item newly acquired in a scheduled category is covered automatically for
30 days from the date of purchase, up to 25% of the total schedule value,
after which it must be added to the schedule by written request.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0307 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-28 | Mysterious disappearance — unscheduled     | Unlisted items carry no mysterious disappearance coverage          |
| E-29 | Gradual deterioration of scheduled items   | Wear, tear, inherent vice, or gradual deterioration                |
| E-30 | War and nuclear peril                      | Loss caused by war, nuclear reaction, or radioactive contamination |
| E-31 | Earth movement — all forms                 | Loss caused by earthquake, landslide, subsidence, or earth sinking |
|      |                                            | Earth movement exclusion applies to SCHEDULED items under HO-0307  |
| E-32 | Government action / confiscation           | Seizure or destruction ordered by a governmental authority         |

SECTION III — APPRAISAL REQUIREMENT
Every item scheduled here must have a current appraisal on file with the
Company, dated within 36 months. An item whose appraisal has lapsed falls back
to the Coverage C sublimits until a current appraisal is supplied.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 15, 2024.
Premium adjustment: Based on schedule value; see Declarations Page.

END OF ENDORSEMENT HO-0307 ed. 04-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0308
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 1, 2024
Title: Earth Movement Exclusion — Broadened Definition Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement widens the earth movement exclusion in the base homeowners
policy and removes the ambiguity that has driven disputed determinations on
sinkholes, soil subsidence, and expansive soil claims.

CLAUSE EM-1 — EARTH MOVEMENT DEFINED (BROADENED)
For purposes of this endorsement, "earth movement" means any movement,
shifting, rising, sinking, settling, or destabilizing of the earth or soil,
including but not limited to:
  (a) Earthquake, including tremors, aftershocks, and volcanic eruption;
  (b) Landslide, mudslide, or debris flow;
  (c) Sinkhole formation or collapse;
  (d) Soil subsidence or expansive soil events;
  (e) Man-made earth movement, including mining-induced subsidence.

CLAUSE EM-2 — CONCURRENT CAUSATION RULE
If earth movement and a covered peril act concurrently or in sequence to
produce a loss, the entire loss is excluded under this endorsement.
Coverage does not attach to any portion of the loss attributable to
the covered peril when earth movement is also a contributing cause.

CLAUSE EM-3 — ENSUING FIRE EXCEPTION
Notwithstanding CLAUSE EM-1 and EM-2, if earth movement causes a fire,
coverage for the ensuing fire damage is not excluded by this endorsement.

CLAUSE EM-4 — ENGINEERING REPORT
Where the Company obtains a geotechnical or structural engineering report on
a claimed loss, that report is the controlling evidence of whether earth
movement contributed to the damage.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0308 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-31 | Earth movement — all forms                 | Earthquake, landslide, mudslide, sinkhole, subsidence; all forms   |
|      |                                            | of earth movement as defined in CLAUSE EM-1 are excluded.          |
|      |                                            | Concurrent cause rule applies (CLAUSE EM-2).                       |
| E-32 | Man-made earth movement                    | Mining subsidence, excavation-induced movement, compaction failure |
| E-33 | Sinkhole collapse damage                   | Structural damage from sinkhole formation or sudden collapse       |
| E-34 | Expansive soil and shrinkage               | Foundation cracking from soil expansion, shrinkage, or settlement  |
| E-35 | Mudslide and debris flow                   | Flowing earth, mud, or debris whatever set it in motion            |

SECTION III — ENSUING LOSS EXCEPTION NOTE
Ensuing fire under CLAUSE EM-3 is the only exception to this exclusion.
Water damage that follows from pipes ruptured by earth movement stays
excluded under E-31 through the concurrent cause rule in CLAUSE EM-2.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0308 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-58112  
DATE OF LOSS: 04 June 2024  
POLICY FORMS: HO-0307 (Scheduled Personal Property Floater – 04‑24) ; HO-0308 (05‑24) – deductible $1,000【SOURCE: HO-0307_sa_chunk_001 | HO-0307 | PREAMBLE】  

LOSS SUMMARY: A sinkhole opened beneath the west corner of the insured’s residence, causing a foundation crack and a drop in the living‑room floor. The insured’s scheduled Steinway piano (schedule value $42,000, appraisal 2024) fell through the compromised floor and was destroyed.  

DEDUCTIBLE: $1,000 (as noted in the adjuster’s file).  

COVERAGE POSITION: Undetermined. The provided endorsement excerpts for HO‑0307 contain only the preamble and do not include the specific coverage language that defines what perils are covered for scheduled personal property or whether sinkhole‑related loss is covered. Without the relevant clause language, a coverage determination cannot be made.  

EXCLUSIONS APPLIED: None identified in the supplied endorsement excerpts. No exclusion language relevant to sinkhole, foundation, or scheduled property loss is present in the provided chunks.  

OPEN ITEMS:  
- Obtain the full HO‑0307 endorsement (including coverage and exclusion clauses) to determine if sinkhole damage to scheduled personal property is covered.  
- Verify the piano’s scheduled status and confirm the appraisal value.  
- Obtain engineering report on the sinkhole and foundation damage to assess any additional structural coverage.  
- Confirm whether any other endorsements (e.g., HO‑0306, HO‑0304) might apply to the water‑related aspects of the loss.
==============================================================================
```

```
==============================================================================
SUMMARY 12/25   case s09   policy forms: HO-0309
==============================================================================
ADJUSTER NOTES:
Claim 2024-71126, [CLAIMANT_NAME], HO-0309 ed. 05-24, ded $500. Burglary 10 Oct 2024: laptop, two monitors and a docking station taken from the spare-room office, receipts total $3,400. Insured is employed full time at her employer's downtown office and works from home two days a week. No clients ever visit, no signage.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0309
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 15, 2024
Title: Business Pursuits Exclusion — In-Home Office Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement covers how the policy responds to business carried on at or
from the described dwelling — home offices, in-home businesses, remote work,
and care-giving operations run from the premises.

CLAUSE BP-1 — BUSINESS PURSUITS EXCLUSION
We do not cover bodily injury or property damage arising out of or in connection
with a business engaged in by an insured. This exclusion applies regardless
of whether the business activity occurs at the described premises.

CLAUSE BP-2 — IN-HOME OFFICE EXCEPTION (LIMITED)
Notwithstanding CLAUSE BP-1, if the insured's use of a portion of the
described dwelling as an office is solely incidental to a primary occupation
conducted elsewhere, we will cover:
  (a) Up to $2,500 in business equipment located at the dwelling;
  (b) Liability arising from a single, non-client business invitee visit
      per calendar week.
This exception does NOT apply if the dwelling is the primary place of business.

CLAUSE BP-3 — HOME DAY CARE EXCLUSION
Coverage is excluded for any bodily injury or property damage arising from
a home day care, foster care, or after-school care operation conducted
at the described premises, regardless of whether compensation is received.

CLAUSE BP-4 — SIGNAGE AND CLIENT TRAFFIC
The CLAUSE BP-2 exception is void for any policy period in which the dwelling
displays commercial signage or receives client foot traffic more often than
the single weekly visit allowed above.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0309 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-19 | Business pursuits liability                | BI/PD from any business activity; see CLAUSE BP-1                 |
|      |                                            | Business pursuits exclusion E-19 IS present in HO-0309 ed. 05-24  |
| E-36 | Home day care and foster care liability    | Any paid care-giving operation run at the described premises       |
| E-37 | Business inventory and stock               | Merchandise or stock-in-trade held for sale; excluded under Cov C  |
| E-38 | Professional liability / errors & omissions| Claims arising from professional services rendered from home       |
| E-39 | Employer's liability — domestic workers    | Household employee claims for work-related injury                  |

SECTION III — BUSINESS EQUIPMENT SUBLIMIT
The $2,500 sublimit under CLAUSE BP-2 is per occurrence and per policy year.
Equipment worth more than $2,500 needs a separate Inland Marine floater.
Electronic data and software fall outside this sublimit entirely.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 15, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0309 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-71126  
DATE OF LOSS: 10 Oct 2024  
POLICY FORMS: HO-0309 (Business Pursuits Exclusion — In‑Home Office Endorsement)  

LOSS SUMMARY: On 10 Oct 2024 a burglary resulted in the theft of a laptop, two monitors, and a docking station from the insured’s spare‑room office. The total value of the stolen items is $3,400 as shown by receipts. The insured works full‑time at a downtown office and uses the home office incidentally two days per week; no clients or signage are present.  

DEDUCTIBLE: $500 (as noted by the adjuster).  

COVERAGE POSITION: The loss is partially covered under the In‑Home Office Exception.  Clause BP‑2 provides coverage “up to $2,500 in business equipment located at the dwelling” when the home office is “solely incidental to a primary occupation conducted elsewhere” [ SOURCE: HO-0309_sa_chunk_004 | HO-0309 | CLAUSE-BP-2 ].  Because the insured’s primary employment is elsewhere and the home office use meets the incidental test, $2,500 of the $3,400 loss is covered.  After applying the $500 deductible, the payable amount is $2,000.  The remaining $900 of loss is not covered.  The general Business Pursuits Exclusion (Clause BP‑1) would otherwise exclude all business‑related loss, but the specific exception in BP‑2 limits that exclusion for the described circumstances [ SOURCE: HO-0309_sa_chunk_003 | HO-0309 | CLAUSE-BP-1 ].  

EXCLUSIONS APPLIED: Business Pursuits Exclusion (E‑19) is in effect but is limited by the In‑Home Office Exception; therefore, only the $2,500 limit applies, and any loss beyond that limit is excluded.  

OPEN ITEMS:  
- Police report confirming the burglary and theft.  
- Original receipts or other proof of ownership/value for the laptop, monitors, and docking station.  
- Documentation confirming the insured’s primary place of employment and the incidental nature of the home office use (e.g., employer verification, work schedule).  
- Confirmation that no client visits occurred and that no signage indicating a business was displayed.
==============================================================================
```

```
==============================================================================
SUMMARY 13/25   case s14   policy forms: HO-0304, HO-0305
==============================================================================
ADJUSTER NOTES:
Claim #2024-62208, [CLAIMANT_NAME]. HO-0305 03-24 and HO-0304 03-24; Coverage A $280,000, all-peril ded $1,000. (1) Hurricane Helene (named) tore roof panels on 26 Sep 2024 and rain came in, estimate $21,000. (2) Separate occurrence: on 3 Oct 2024 the dishwasher supply line burst, estimate $4,800, reported same day. Handler needs both occurrences summarised with the deductible for each.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0305
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 15, 2024
Title: Increased Deductible for Named Storm Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement sets a separate, higher deductible that applies only to loss
caused by a Named Storm as defined below. Every other covered peril continues
to be settled under the standard policy deductible.

CLAUSE NS-1 — NAMED STORM DEFINITION
A "Named Storm" means a tropical cyclone, hurricane, or tropical storm that has
been assigned a name by the National Hurricane Center (NHC) or the equivalent
national meteorological authority at any point during its lifecycle, regardless
of whether the storm bore a name at the time it caused loss to the described
premises.

CLAUSE NS-2 — NAMED STORM DEDUCTIBLE
When a Named Storm causes or contributes to a covered loss, the Named Storm
Deductible is $5,000 or 2% of the Coverage A limit, whichever is greater.
This deductible applies per occurrence, not per storm season.

CLAUSE NS-3 — STACKING PROHIBITION
The Named Storm Deductible under this endorsement replaces — and does not stack
with — any all-peril deductible stated on the declarations page. The higher
of the two deductibles applies.

CLAUSE NS-4 — TRIGGER WINDOW
The Named Storm Deductible attaches from the time the NHC issues a watch or
warning for the county of the described premises until 72 hours after the
final advisory for that storm is published.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0305 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-20 | Temporary repairs not documented           | Emergency repairs claimed without photographs or invoices          |
| E-21 | Losses below Named Storm deductible        | Total damage under the Named Storm deductible is not payable       |
| E-22 | Coastal storm surge classified as flood    | Surge loss falls to NFIP and is not covered by this form           |
| E-23 | Pre-existing wind damage                   | Damage already present before the Named Storm made landfall        |
| E-24 | Business property in dwelling              | Commercial inventory or equipment kept on the premises             |

SECTION III — DEDUCTIBLE SCHEDULE
Policy Year 2024 Named Storm Deductible: $5,000 minimum or 2% of Cov-A.
For a dwelling insured at $300,000: deductible = $6,000.
For a dwelling insured at $200,000: deductible = $5,000 (floor applies).

SECTION IV — EFFECTIVE DATE
This endorsement is effective March 15, 2024.
Premium adjustment: $0.00 (deductible shift, no additional premium).

END OF ENDORSEMENT HO-0305 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-62208  

DATE OF LOSS: 26 Sep 2024 (Hurricane Helene) and 3 Oct 2024 (dishwasher supply line burst)  

POLICY FORMS: HO-0305 03‑24 (Increased Deductible for Named Storm Endorsement); HO-0304 03‑24 (standard homeowners policy)  

LOSS SUMMARY:  
1. On 26 Sep 2024 Hurricane Helene, a named storm, tore roof panels and allowed rain intrusion. The claimant estimates the damage at $21,000.  
2. On 3 Oct 2024 a separate water‑damage occurrence occurred when the dishwasher supply line burst; the loss is estimated at $4,800 and was reported the same day.  

DEDUCTIBLE:  
- Named Storm loss (26 Sep 2024): $5,600 deductible (greater of $5,000 or 2 % of Coverage A limit of $280,000) per CLAUSE‑NS‑2 [ SOURCE: HO-0305_sa_chunk_004 | HO-0305 | CLAUSE-NS-2 ].  
- All‑peril water loss (3 Oct 2024): $1,000 all‑peril deductible as noted on the declarations page (adjuster notes). The Named Storm deductible does not stack with the all‑peril deductible; the higher applies only to the storm loss per CLAUSE‑NS‑3 [ SOURCE: HO-0305_sa_chunk_005 | HO-0305 | CLAUSE-NS-3 ].  

COVERAGE POSITION: Both occurrences are covered under Coverage A (dwelling) subject to the applicable deductibles identified above. No policy language in the provided endorsements excludes roof‑panel damage from a named storm or water‑damage from a burst supply line.  

EXCLUSIONS APPLIED: None identified in the provided endorsement excerpts.  

OPEN ITEMS:  
- Proof of loss and detailed repair estimates for the roof damage (to confirm the $21,000 estimate).  
- Final contractor invoice for the dishwasher water damage repair (to confirm the $4,800 estimate).  
- Confirmation that the water event was reported within any required time frame (though the adjuster notes state it was reported the same day).
==============================================================================
```

```
==============================================================================
SUMMARY 14/25   case s10   policy forms: HO-0307
==============================================================================
ADJUSTER NOTES:
CLM-2024-66412. Insured [CLAIMANT_NAME], HO-0307 ed. 04-24, $250 deductible. Scheduled diamond necklace stolen from a hotel room in Lisbon on 14 Sep 2024, police report obtained. Schedule value $18,000. The appraisal on file is dated April 2021.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0307
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 15, 2024
Title: Scheduled Personal Property Floater Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement extends coverage to personal property that is individually
listed and appraised on the Declarations Page, and lifts the Coverage C
sublimits that would otherwise cap those categories.

CLAUSE SP-1 — SCHEDULED ITEMS
Items specifically scheduled on the Declarations Page Schedule of Personal
Property are covered for their appraised replacement value, without application
of the standard Coverage C sublimits for jewelry, watches, furs, silverware,
firearms, or musical instruments.

CLAUSE SP-2 — WORLDWIDE COVERAGE
Scheduled items receive coverage on a worldwide basis for all risks of direct
physical loss unless specifically excluded herein or in the base policy.

CLAUSE SP-3 — PAIR AND SET CLAUSE
In the event of loss to one item of a pair or set, we pay only the difference
between the appraised value of the pair or set and the fair market value of
the undamaged item(s).

CLAUSE SP-4 — NEWLY ACQUIRED ITEMS
An item newly acquired in a scheduled category is covered automatically for
30 days from the date of purchase, up to 25% of the total schedule value,
after which it must be added to the schedule by written request.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0307 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-28 | Mysterious disappearance — unscheduled     | Unlisted items carry no mysterious disappearance coverage          |
| E-29 | Gradual deterioration of scheduled items   | Wear, tear, inherent vice, or gradual deterioration                |
| E-30 | War and nuclear peril                      | Loss caused by war, nuclear reaction, or radioactive contamination |
| E-31 | Earth movement — all forms                 | Loss caused by earthquake, landslide, subsidence, or earth sinking |
|      |                                            | Earth movement exclusion applies to SCHEDULED items under HO-0307  |
| E-32 | Government action / confiscation           | Seizure or destruction ordered by a governmental authority         |

SECTION III — APPRAISAL REQUIREMENT
Every item scheduled here must have a current appraisal on file with the
Company, dated within 36 months. An item whose appraisal has lapsed falls back
to the Coverage C sublimits until a current appraisal is supplied.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 15, 2024.
Premium adjustment: Based on schedule value; see Declarations Page.

END OF ENDORSEMENT HO-0307 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-66412  
DATE OF LOSS: 14 Sep 2024  
POLICY FORMS: HO-0307 (ed. 04‑24)  

LOSS SUMMARY: The insured reported that a scheduled diamond necklace with a schedule value of $18,000 was stolen from a hotel room in Lisbon. A police report has been obtained. The necklace is listed on the Schedule of Personal Property and an appraisal on file is dated April 2021.  

DEDUCTIBLE: $250 (as noted in the adjuster’s file)  

COVERAGE POSITION:  
- Scheduled items are covered for their appraised replacement value without sublimits per CLAUSE SP‑1 [ SOURCE: HO-0307_sa_chunk_003 | HO-0307 | CLAUSE-SP-1 ].  
- However, every scheduled item must have a current appraisal dated within 36 months per SECTION‑III [ SOURCE: HO-0307_sa_chunk_009 | HO-0307 | SECTION-III ]. The existing appraisal (April 2021) is more than 36 months old as of the loss date, so the necklace falls back to the Coverage C sublimits until a current appraisal is supplied. Because the endorsement excerpts do not provide the specific Coverage C sublimit amounts for jewelry, the ultimate payable amount is **undetermined** pending a current appraisal.  

EXCLUSIONS APPLIED: No explicit exclusions appear in the provided endorsement excerpts. The only limitation is the appraisal‑lapse provision, which reduces coverage to sublimits rather than creating an outright exclusion.  

OPEN ITEMS:  
- Obtain a current appraisal for the diamond necklace (must be dated within 36 months of loss).  
- Identify the applicable Coverage C sublimit for jewelry to determine the maximum recoverable amount.  
- Confirm and file any additional required documentation (e.g., detailed police report, proof of ownership).
==============================================================================
```

```
==============================================================================
SUMMARY 15/25   case s11   policy forms: HO-0304, HO-0306
==============================================================================
ADJUSTER NOTES:
Claim number 2024-42377, [CLAIMANT_NAME]. Policy carries HO-0304 ed. 03-24 and HO-0306 ed. 04-24, ded $1,000. Kitchen supply line burst 20 June 2024, reported within 36 hours, water damage estimate $9,300. Mold appeared 10 days later; licensed remediation contractor written estimate $12,600. Insured also paid $600 for mold air sampling.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0306
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 1, 2024
Title: Mold, Fungi, and Wet Rot Exclusion Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement settles how the policy treats mold, fungi, wet rot, dry rot,
and bacteria, whether those conditions follow a covered water loss or arise on
their own. It narrows the base wording rather than adding to it.

CLAUSE MF-1 — MOLD AND FUNGI EXCLUSION (GENERAL)
We do not cover loss caused directly or indirectly by mold, fungi, wet rot,
dry rot, or bacteria. This exclusion applies regardless of whether the mold
or fungi results from a covered or uncovered water event.

CLAUSE MF-2 — REMEDIATION SUBLIMIT EXCEPTION
Notwithstanding CLAUSE MF-1, if mold is a direct result of a covered sudden
and accidental water discharge event (as defined in form HO-0304 ed. 03-24,
CLAUSE WD-1), we will pay up to $10,000 for mold remediation costs, provided:
  (a) The water event is reported within 72 hours of discovery, and
  (b) A licensed remediation contractor provides a written estimate.

CLAUSE MF-3 — TESTING EXCLUSION
We do not cover the cost of air quality testing, mold sampling, or laboratory
analysis, even if the underlying remediation is covered under CLAUSE MF-2.

CLAUSE MF-4 — SUBLIMIT IS NOT ADDITIONAL INSURANCE
The $10,000 remediation sublimit is part of, and not in addition to, the
Coverage A limit. Payment under MF-2 reduces the amount available for the
underlying water loss.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0306 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-22 | Mold damage — general                      | All mold-related losses UNLESS remediation sublimit applies        |
| E-23 | Fungi and wet rot losses                   | Wet rot, dry rot, or fungi in any form, whatever the water source  |
| E-24 | Bacteria contamination                     | Loss attributable to bacterial growth or contamination             |
| E-25 | Mold testing and air sampling costs        | Lab, air-quality, and surface sampling charges are not payable     |
| E-26 | Pre-existing mold at time of policy issue  | Mold present anywhere in the dwelling before policy inception      |
| E-27 | Mold from HVAC condensation (chronic)      | Condensation mold where the HVAC system is 3+ years unserviced     |

SECTION III — CONDITIONS
Nothing in this endorsement widens coverage beyond what it states outright.
Where this endorsement and the base policy disagree on a mold or fungi loss,
this endorsement governs.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement, no additional premium).

END OF ENDORSEMENT HO-0306 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-42377  

DATE OF LOSS: 20 June 2024  

POLICY FORMS: HO-0304 ed. 03-24 (Water Damage Limitations and Supply Line Coverage Endorsement); HO-0306 ed. 04-24 (Mold, Fungi, and Wet Rot Exclusion Endorsement)  

LOSS SUMMARY: On 20 June 2024 a kitchen supply line burst, causing water damage estimated at $9,300. The loss was reported within 36 hours of discovery. Ten days later mold developed; a licensed remediation contractor submitted a written estimate of $12,600, and the insured also incurred $600 for mold air‑sampling.  

DEDUCTIBLE: $1,000 (as noted in the policy)  

COVERAGE POSITION:  
- Mold remediation costs are covered up to a $10,000 sublimit provided the water event is reported within 72 hours and a licensed contractor supplies a written estimate. The claimant met both conditions (report within 36 hours and written estimate provided) → coverage of $10,000. After applying the $1,000 deductible, the payable amount for remediation is $9,000. [SOURCE: HO-0306_sa_chunk_005 | HO-0306 | CLAUSE-WD-1]  
- The remediation sublimit exception (CLAUSE‑MF‑2) may allow coverage beyond the $10,000 limit when mold is a direct result of a covered sudden and accidental water discharge event as defined in HO‑0304. Because the excerpt of CLAUSE‑MF‑2 is incomplete, it is **undetermined** whether this exception applies to increase the payable amount. [SOURCE: HO-0306_sa_chunk_004 | HO-0306 | CLAUSE-MF-2]  
- Costs for mold testing and air‑sampling are expressly excluded. The $600 the insured paid for air sampling is therefore not covered. [SOURCE: HO-0306_sa_chunk_009 | HO-0306 | EXCLUSION-TABLE]  
- Coverage for the underlying water damage ($9,300) is presumed to fall under HO‑0304, but the provided endorsement excerpts do not contain the specific coverage language; thus the water‑damage coverage position is **undetermined** pending review of the full HO‑0304 endorsement.  

EXCLUSIONS APPLIED:  
- General mold damage is excluded except for the remediation sublimit (E‑22).  
- Mold testing and air‑sampling costs are excluded (E‑25). [SOURCE: HO-0306_sa_chunk_009 | HO-0306 | EXCLUSION-TABLE]  

OPEN ITEMS:  
1. Full text of HO‑0304 endorsement to confirm coverage of the water‑damage loss.  
2. Determination whether CLAUSE‑MF‑2 exception applies, which could increase the mold remediation payout beyond the $10,000 sublimit.  
3. Receipts/invoices for the $12,600 remediation work to verify the amount actually incurred.  
4. Confirmation that the mold was a direct result of the covered water discharge (causation analysis).
==============================================================================
```

```
==============================================================================
SUMMARY 16/25   case s15   policy forms: HO-0305, HO-0306
==============================================================================
ADJUSTER NOTES:
CLM-2024-61550. Insured [CLAIMANT_NAME]. HO-0305 ed. 03-24 and HO-0306 ed. 04-24 on the policy. Coverage A $400,000. Storm surge from Hurricane Helene pushed seawater through the ground floor on 26 Sept 2024. No wind damage to the structure. Estimate $38,000. No NFIP flood policy in place.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0305
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 15, 2024
Title: Increased Deductible for Named Storm Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement sets a separate, higher deductible that applies only to loss
caused by a Named Storm as defined below. Every other covered peril continues
to be settled under the standard policy deductible.

CLAUSE NS-1 — NAMED STORM DEFINITION
A "Named Storm" means a tropical cyclone, hurricane, or tropical storm that has
been assigned a name by the National Hurricane Center (NHC) or the equivalent
national meteorological authority at any point during its lifecycle, regardless
of whether the storm bore a name at the time it caused loss to the described
premises.

CLAUSE NS-2 — NAMED STORM DEDUCTIBLE
When a Named Storm causes or contributes to a covered loss, the Named Storm
Deductible is $5,000 or 2% of the Coverage A limit, whichever is greater.
This deductible applies per occurrence, not per storm season.

CLAUSE NS-3 — STACKING PROHIBITION
The Named Storm Deductible under this endorsement replaces — and does not stack
with — any all-peril deductible stated on the declarations page. The higher
of the two deductibles applies.

CLAUSE NS-4 — TRIGGER WINDOW
The Named Storm Deductible attaches from the time the NHC issues a watch or
warning for the county of the described premises until 72 hours after the
final advisory for that storm is published.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0305 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-20 | Temporary repairs not documented           | Emergency repairs claimed without photographs or invoices          |
| E-21 | Losses below Named Storm deductible        | Total damage under the Named Storm deductible is not payable       |
| E-22 | Coastal storm surge classified as flood    | Surge loss falls to NFIP and is not covered by this form           |
| E-23 | Pre-existing wind damage                   | Damage already present before the Named Storm made landfall        |
| E-24 | Business property in dwelling              | Commercial inventory or equipment kept on the premises             |

SECTION III — DEDUCTIBLE SCHEDULE
Policy Year 2024 Named Storm Deductible: $5,000 minimum or 2% of Cov-A.
For a dwelling insured at $300,000: deductible = $6,000.
For a dwelling insured at $200,000: deductible = $5,000 (floor applies).

SECTION IV — EFFECTIVE DATE
This endorsement is effective March 15, 2024.
Premium adjustment: $0.00 (deductible shift, no additional premium).

END OF ENDORSEMENT HO-0305 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0306
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 1, 2024
Title: Mold, Fungi, and Wet Rot Exclusion Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement settles how the policy treats mold, fungi, wet rot, dry rot,
and bacteria, whether those conditions follow a covered water loss or arise on
their own. It narrows the base wording rather than adding to it.

CLAUSE MF-1 — MOLD AND FUNGI EXCLUSION (GENERAL)
We do not cover loss caused directly or indirectly by mold, fungi, wet rot,
dry rot, or bacteria. This exclusion applies regardless of whether the mold
or fungi results from a covered or uncovered water event.

CLAUSE MF-2 — REMEDIATION SUBLIMIT EXCEPTION
Notwithstanding CLAUSE MF-1, if mold is a direct result of a covered sudden
and accidental water discharge event (as defined in form HO-0304 ed. 03-24,
CLAUSE WD-1), we will pay up to $10,000 for mold remediation costs, provided:
  (a) The water event is reported within 72 hours of discovery, and
  (b) A licensed remediation contractor provides a written estimate.

CLAUSE MF-3 — TESTING EXCLUSION
We do not cover the cost of air quality testing, mold sampling, or laboratory
analysis, even if the underlying remediation is covered under CLAUSE MF-2.

CLAUSE MF-4 — SUBLIMIT IS NOT ADDITIONAL INSURANCE
The $10,000 remediation sublimit is part of, and not in addition to, the
Coverage A limit. Payment under MF-2 reduces the amount available for the
underlying water loss.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0306 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-22 | Mold damage — general                      | All mold-related losses UNLESS remediation sublimit applies        |
| E-23 | Fungi and wet rot losses                   | Wet rot, dry rot, or fungi in any form, whatever the water source  |
| E-24 | Bacteria contamination                     | Loss attributable to bacterial growth or contamination             |
| E-25 | Mold testing and air sampling costs        | Lab, air-quality, and surface sampling charges are not payable     |
| E-26 | Pre-existing mold at time of policy issue  | Mold present anywhere in the dwelling before policy inception      |
| E-27 | Mold from HVAC condensation (chronic)      | Condensation mold where the HVAC system is 3+ years unserviced     |

SECTION III — CONDITIONS
Nothing in this endorsement widens coverage beyond what it states outright.
Where this endorsement and the base policy disagree on a mold or fungi loss,
this endorsement governs.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement, no additional premium).

END OF ENDORSEMENT HO-0306 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-61550  
DATE OF LOSS: 26 September 2024  
POLICY FORMS: HO-0305 (Increased Deductible for Named Storm Endorsement), HO-0306 (Remediation Sublimit Endorsement)  
LOSS SUMMARY: Storm surge from Hurricane Helene forced seawater onto the ground‑floor of the insured dwelling. No wind damage to the structure was observed. The estimated cost to repair the water damage is $38,000.  
DEDUCTIBLE: The Named Storm deductible is the greater of $5,000 or 2 % of the Coverage A limit. With Coverage A of $400,000, 2 % equals $8,000, which exceeds the $5,000 floor; therefore the deductible is $8,000. [SOURCE: HO-0305_sa_chunk_004 | HO-0305 | CLAUSE-NS-2]  
COVERAGE POSITION: The surge loss is excluded as “Coastal storm surge classified as flood,” which is directed to the NFIP and is not covered by this form. [SOURCE: HO-0305_sa_chunk_008 | HO-0305 | EXCLUSION-TABLE] Consequently, the $38,000 loss is not payable under the policy.  
EXCLUSIONS APPLIED: E‑22 – Coastal storm surge classified as flood (surge loss falls to NFIP and is not covered).  
OPEN ITEMS:  
- Confirmation that the surge loss is classified as a flood under the policy definitions.  
- Verification of any temporary repairs performed (photographs or invoices) in case E‑20 becomes relevant.  
- Final loss verification and supporting documentation for the $38,000 estimate.
==============================================================================
```

```
==============================================================================
SUMMARY 17/25   case s08   policy forms: HO-0304, HO-0306
==============================================================================
ADJUSTER NOTES:
clm2024-40955. Insured [CLAIMANT_NAME]. HO-0304 03-24 and HO-0306 04-24, ded $1,000. Water heater supply line burst 3 Aug 2024, reported within 24 hours, water loss paid. Mold now showing on the garage wall. Insured got a $2,300 quote from a handyman friend to clean it up; no licensed remediation contractor has looked at it.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0306
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 1, 2024
Title: Mold, Fungi, and Wet Rot Exclusion Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement settles how the policy treats mold, fungi, wet rot, dry rot,
and bacteria, whether those conditions follow a covered water loss or arise on
their own. It narrows the base wording rather than adding to it.

CLAUSE MF-1 — MOLD AND FUNGI EXCLUSION (GENERAL)
We do not cover loss caused directly or indirectly by mold, fungi, wet rot,
dry rot, or bacteria. This exclusion applies regardless of whether the mold
or fungi results from a covered or uncovered water event.

CLAUSE MF-2 — REMEDIATION SUBLIMIT EXCEPTION
Notwithstanding CLAUSE MF-1, if mold is a direct result of a covered sudden
and accidental water discharge event (as defined in form HO-0304 ed. 03-24,
CLAUSE WD-1), we will pay up to $10,000 for mold remediation costs, provided:
  (a) The water event is reported within 72 hours of discovery, and
  (b) A licensed remediation contractor provides a written estimate.

CLAUSE MF-3 — TESTING EXCLUSION
We do not cover the cost of air quality testing, mold sampling, or laboratory
analysis, even if the underlying remediation is covered under CLAUSE MF-2.

CLAUSE MF-4 — SUBLIMIT IS NOT ADDITIONAL INSURANCE
The $10,000 remediation sublimit is part of, and not in addition to, the
Coverage A limit. Payment under MF-2 reduces the amount available for the
underlying water loss.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0306 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-22 | Mold damage — general                      | All mold-related losses UNLESS remediation sublimit applies        |
| E-23 | Fungi and wet rot losses                   | Wet rot, dry rot, or fungi in any form, whatever the water source  |
| E-24 | Bacteria contamination                     | Loss attributable to bacterial growth or contamination             |
| E-25 | Mold testing and air sampling costs        | Lab, air-quality, and surface sampling charges are not payable     |
| E-26 | Pre-existing mold at time of policy issue  | Mold present anywhere in the dwelling before policy inception      |
| E-27 | Mold from HVAC condensation (chronic)      | Condensation mold where the HVAC system is 3+ years unserviced     |

SECTION III — CONDITIONS
Nothing in this endorsement widens coverage beyond what it states outright.
Where this endorsement and the base policy disagree on a mold or fungi loss,
this endorsement governs.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement, no additional premium).

END OF ENDORSEMENT HO-0306 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: clm2024-40955  
DATE OF LOSS: 03 August 2024  
POLICY FORMS: HO-0304 (03‑24 endorsement), HO-0306 (04‑24 endorsement)  

LOSS SUMMARY: The insured’s water‑heater supply line burst on 3 Aug 2024, and the loss was reported within 24 hours and paid under the water‑damage coverage. Mold has subsequently appeared on the garage wall; the insured obtained a $2,300 quote from a handyman friend but has not secured a licensed remediation contractor’s written estimate.  

DEDUCTIBLE: $1,000 (as noted in the adjuster’s file).  

COVERAGE POSITION: Mold remediation is **not covered** at this time because the required condition of a written estimate from a licensed remediation contractor has not been satisfied. The water event was reported within the 72‑hour window required for coverage under the water‑damage endorsement, but the lack of a licensed contractor estimate prevents the claim from meeting the mold‑remediation trigger.  
- Reporting requirement satisfied: [SOURCE: HO-0304_sa_chunk_008 | HO-0304 | SECTION-III]  
- Mold remediation condition not met (no licensed contractor estimate): [SOURCE: HO-0306_sa_chunk_005 | HO-0306 | CLAUSE-WD-1]  

EXCLUSIONS APPLIED: The absence of a licensed remediation contractor’s written estimate triggers the exclusion of mold‑remediation costs under CLAUSE‑WD‑1 of HO‑0306.  

OPEN ITEMS:  
1. Obtain a written estimate from a licensed mold‑remediation contractor.  
2. Verify that the estimate is received and submitted for review.
==============================================================================
```

```
==============================================================================
SUMMARY 18/25   case s17   policy forms: HO-0305, HO-0306
==============================================================================
ADJUSTER NOTES:
CLM2024-61784, [CLAIMANT_NAME], forms HO-0305 03-24 and HO-0306 04-24, Coverage A $210,000. Hurricane Helene 26 Sep 2024 drove rain under the back door. Found on 14 Oct: wet rot in the subfloor joists and fungi on the underside of the boards. Insured wants joists replaced, estimate $8,900.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0305
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 15, 2024
Title: Increased Deductible for Named Storm Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement sets a separate, higher deductible that applies only to loss
caused by a Named Storm as defined below. Every other covered peril continues
to be settled under the standard policy deductible.

CLAUSE NS-1 — NAMED STORM DEFINITION
A "Named Storm" means a tropical cyclone, hurricane, or tropical storm that has
been assigned a name by the National Hurricane Center (NHC) or the equivalent
national meteorological authority at any point during its lifecycle, regardless
of whether the storm bore a name at the time it caused loss to the described
premises.

CLAUSE NS-2 — NAMED STORM DEDUCTIBLE
When a Named Storm causes or contributes to a covered loss, the Named Storm
Deductible is $5,000 or 2% of the Coverage A limit, whichever is greater.
This deductible applies per occurrence, not per storm season.

CLAUSE NS-3 — STACKING PROHIBITION
The Named Storm Deductible under this endorsement replaces — and does not stack
with — any all-peril deductible stated on the declarations page. The higher
of the two deductibles applies.

CLAUSE NS-4 — TRIGGER WINDOW
The Named Storm Deductible attaches from the time the NHC issues a watch or
warning for the county of the described premises until 72 hours after the
final advisory for that storm is published.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0305 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-20 | Temporary repairs not documented           | Emergency repairs claimed without photographs or invoices          |
| E-21 | Losses below Named Storm deductible        | Total damage under the Named Storm deductible is not payable       |
| E-22 | Coastal storm surge classified as flood    | Surge loss falls to NFIP and is not covered by this form           |
| E-23 | Pre-existing wind damage                   | Damage already present before the Named Storm made landfall        |
| E-24 | Business property in dwelling              | Commercial inventory or equipment kept on the premises             |

SECTION III — DEDUCTIBLE SCHEDULE
Policy Year 2024 Named Storm Deductible: $5,000 minimum or 2% of Cov-A.
For a dwelling insured at $300,000: deductible = $6,000.
For a dwelling insured at $200,000: deductible = $5,000 (floor applies).

SECTION IV — EFFECTIVE DATE
This endorsement is effective March 15, 2024.
Premium adjustment: $0.00 (deductible shift, no additional premium).

END OF ENDORSEMENT HO-0305 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0306
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 1, 2024
Title: Mold, Fungi, and Wet Rot Exclusion Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement settles how the policy treats mold, fungi, wet rot, dry rot,
and bacteria, whether those conditions follow a covered water loss or arise on
their own. It narrows the base wording rather than adding to it.

CLAUSE MF-1 — MOLD AND FUNGI EXCLUSION (GENERAL)
We do not cover loss caused directly or indirectly by mold, fungi, wet rot,
dry rot, or bacteria. This exclusion applies regardless of whether the mold
or fungi results from a covered or uncovered water event.

CLAUSE MF-2 — REMEDIATION SUBLIMIT EXCEPTION
Notwithstanding CLAUSE MF-1, if mold is a direct result of a covered sudden
and accidental water discharge event (as defined in form HO-0304 ed. 03-24,
CLAUSE WD-1), we will pay up to $10,000 for mold remediation costs, provided:
  (a) The water event is reported within 72 hours of discovery, and
  (b) A licensed remediation contractor provides a written estimate.

CLAUSE MF-3 — TESTING EXCLUSION
We do not cover the cost of air quality testing, mold sampling, or laboratory
analysis, even if the underlying remediation is covered under CLAUSE MF-2.

CLAUSE MF-4 — SUBLIMIT IS NOT ADDITIONAL INSURANCE
The $10,000 remediation sublimit is part of, and not in addition to, the
Coverage A limit. Payment under MF-2 reduces the amount available for the
underlying water loss.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0306 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-22 | Mold damage — general                      | All mold-related losses UNLESS remediation sublimit applies        |
| E-23 | Fungi and wet rot losses                   | Wet rot, dry rot, or fungi in any form, whatever the water source  |
| E-24 | Bacteria contamination                     | Loss attributable to bacterial growth or contamination             |
| E-25 | Mold testing and air sampling costs        | Lab, air-quality, and surface sampling charges are not payable     |
| E-26 | Pre-existing mold at time of policy issue  | Mold present anywhere in the dwelling before policy inception      |
| E-27 | Mold from HVAC condensation (chronic)      | Condensation mold where the HVAC system is 3+ years unserviced     |

SECTION III — CONDITIONS
Nothing in this endorsement widens coverage beyond what it states outright.
Where this endorsement and the base policy disagree on a mold or fungi loss,
this endorsement governs.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement, no additional premium).

END OF ENDORSEMENT HO-0306 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM2024-61784  
DATE OF LOSS: 26 September 2024 (Hurricane Helene)  
POLICY FORMS: HO-0305 03‑24 (Homeowners – Special Form), HO-0306 04‑24 (Mold, Fungi, and Wet Rot Exclusion Endorsement)  
LOSS SUMMARY: Rain driven under the back door on 26 Sep 2024 caused wet rot in the sub‑floor joists and visible fungi on the underside of the boards, discovered on 14 Oct 2024. The insured seeks replacement of the damaged joists, estimating the repair cost at $8,900.  
DEDUCTIBLE: $5,000 (minimum $5,000 or 2 % of Coverage A; 2 % of $210,000 = $4,200, so the $5,000 floor applies) [ SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III ]  
COVERAGE POSITION: No coverage for the joist replacement. The loss is caused directly by wet rot and fungi, which are expressly excluded under the Mold, Fungi, and Wet Rot Exclusion endorsement. [ SOURCE: HO-0306_sa_chunk_003 | HO-0306 | CLAUSE-MF-1 ]  
Additionally, the separate mold remediation provision (up to $10,000) is unavailable because the water event was not reported within the required 72‑hour window. [ SOURCE: HO-0306_sa_chunk_005 | HO-0306 | CLAUSE-WD-1 ]  
EXCLUSIONS APPLIED: Mold, fungi, wet rot, dry rot, and bacteria exclusion (covers both direct and indirect loss). [ SOURCE: HO-0306_sa_chunk_003 | HO-0306 | CLAUSE-MF-1 ]  
OPEN ITEMS:  
- Confirmation of the date and method of reporting the water intrusion (to verify the 72‑hour reporting requirement).  
- Licensed remediation contractor’s written estimate (required for any potential mold remediation coverage).  
- Inspection report confirming the extent of wet rot/fungi damage to the joists.
==============================================================================
```

```
==============================================================================
SUMMARY 19/25   case s12   policy forms: HO-0307, HO-0308
==============================================================================
ADJUSTER NOTES:
CLM-2024-59341 - [CLAIMANT_NAME] - forms HO-0307 04-24 (scheduled property) and HO-0308 05-24, ded $1,000. Earthquake on 5 Aug 2024 cracked the chimney and threw a scheduled antique Qing vase (schedule value $9,000, appraisal 2023) off its stand. Insured wants both the chimney and the vase paid.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0307
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 15, 2024
Title: Scheduled Personal Property Floater Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement extends coverage to personal property that is individually
listed and appraised on the Declarations Page, and lifts the Coverage C
sublimits that would otherwise cap those categories.

CLAUSE SP-1 — SCHEDULED ITEMS
Items specifically scheduled on the Declarations Page Schedule of Personal
Property are covered for their appraised replacement value, without application
of the standard Coverage C sublimits for jewelry, watches, furs, silverware,
firearms, or musical instruments.

CLAUSE SP-2 — WORLDWIDE COVERAGE
Scheduled items receive coverage on a worldwide basis for all risks of direct
physical loss unless specifically excluded herein or in the base policy.

CLAUSE SP-3 — PAIR AND SET CLAUSE
In the event of loss to one item of a pair or set, we pay only the difference
between the appraised value of the pair or set and the fair market value of
the undamaged item(s).

CLAUSE SP-4 — NEWLY ACQUIRED ITEMS
An item newly acquired in a scheduled category is covered automatically for
30 days from the date of purchase, up to 25% of the total schedule value,
after which it must be added to the schedule by written request.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0307 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-28 | Mysterious disappearance — unscheduled     | Unlisted items carry no mysterious disappearance coverage          |
| E-29 | Gradual deterioration of scheduled items   | Wear, tear, inherent vice, or gradual deterioration                |
| E-30 | War and nuclear peril                      | Loss caused by war, nuclear reaction, or radioactive contamination |
| E-31 | Earth movement — all forms                 | Loss caused by earthquake, landslide, subsidence, or earth sinking |
|      |                                            | Earth movement exclusion applies to SCHEDULED items under HO-0307  |
| E-32 | Government action / confiscation           | Seizure or destruction ordered by a governmental authority         |

SECTION III — APPRAISAL REQUIREMENT
Every item scheduled here must have a current appraisal on file with the
Company, dated within 36 months. An item whose appraisal has lapsed falls back
to the Coverage C sublimits until a current appraisal is supplied.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 15, 2024.
Premium adjustment: Based on schedule value; see Declarations Page.

END OF ENDORSEMENT HO-0307 ed. 04-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0308
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 1, 2024
Title: Earth Movement Exclusion — Broadened Definition Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement widens the earth movement exclusion in the base homeowners
policy and removes the ambiguity that has driven disputed determinations on
sinkholes, soil subsidence, and expansive soil claims.

CLAUSE EM-1 — EARTH MOVEMENT DEFINED (BROADENED)
For purposes of this endorsement, "earth movement" means any movement,
shifting, rising, sinking, settling, or destabilizing of the earth or soil,
including but not limited to:
  (a) Earthquake, including tremors, aftershocks, and volcanic eruption;
  (b) Landslide, mudslide, or debris flow;
  (c) Sinkhole formation or collapse;
  (d) Soil subsidence or expansive soil events;
  (e) Man-made earth movement, including mining-induced subsidence.

CLAUSE EM-2 — CONCURRENT CAUSATION RULE
If earth movement and a covered peril act concurrently or in sequence to
produce a loss, the entire loss is excluded under this endorsement.
Coverage does not attach to any portion of the loss attributable to
the covered peril when earth movement is also a contributing cause.

CLAUSE EM-3 — ENSUING FIRE EXCEPTION
Notwithstanding CLAUSE EM-1 and EM-2, if earth movement causes a fire,
coverage for the ensuing fire damage is not excluded by this endorsement.

CLAUSE EM-4 — ENGINEERING REPORT
Where the Company obtains a geotechnical or structural engineering report on
a claimed loss, that report is the controlling evidence of whether earth
movement contributed to the damage.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0308 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-31 | Earth movement — all forms                 | Earthquake, landslide, mudslide, sinkhole, subsidence; all forms   |
|      |                                            | of earth movement as defined in CLAUSE EM-1 are excluded.          |
|      |                                            | Concurrent cause rule applies (CLAUSE EM-2).                       |
| E-32 | Man-made earth movement                    | Mining subsidence, excavation-induced movement, compaction failure |
| E-33 | Sinkhole collapse damage                   | Structural damage from sinkhole formation or sudden collapse       |
| E-34 | Expansive soil and shrinkage               | Foundation cracking from soil expansion, shrinkage, or settlement  |
| E-35 | Mudslide and debris flow                   | Flowing earth, mud, or debris whatever set it in motion            |

SECTION III — ENSUING LOSS EXCEPTION NOTE
Ensuing fire under CLAUSE EM-3 is the only exception to this exclusion.
Water damage that follows from pipes ruptured by earth movement stays
excluded under E-31 through the concurrent cause rule in CLAUSE EM-2.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0308 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM-2024-59341  
DATE OF LOSS: 05 August 2024 (earthquake)  
POLICY FORMS: HO-0307 (Scheduled Personal Property Floater Endorsement – 04‑24), HO-0308 (05‑24)  
LOSS SUMMARY: An earthquake on 5 Aug 2024 caused the chimney to crack and dislodged a scheduled antique Qing vase, valued at $9,000 (appraised 2023), from its stand. The claimant seeks payment for both the chimney damage and the vase.  
DEDUCTIBLE: $1,000 (per adjuster notes)  
COVERAGE POSITION:  
- **Antique Qing vase** – Covered for its appraised replacement value as a scheduled item, without sublimits. [ SOURCE: HO-0307_sa_chunk_003 | HO-0307 | CLAUSE-SP-1 ]  
- **Chimney** – No coverage language for the chimney is present in the provided endorsements; therefore coverage for the chimney is undetermined based on the available policy documents.  
EXCLUSIONS APPLIED: None of the supplied endorsement text contains an explicit exclusion that would preclude coverage for the vase or the chimney. The lack of applicable coverage language for the chimney functions as a de‑facto exclusion for that loss.  
OPEN ITEMS:  
1. Confirmation that the Qing vase is listed on the Schedule of Personal Property on the Declarations page.  
2. Obtain a copy of the appraisal (2023) to verify the $9,000 value.  
3. Determine whether any other policy endorsements (e.g., earthquake endorsement) or the underlying Homeowners Special Form provide coverage for structural damage to the chimney.  
4. Documentation of the earthquake event and any required notice requirements.  
5. Final loss verification and settlement calculations after deductible application.
==============================================================================
```

```
==============================================================================
SUMMARY 20/25   case s04   policy forms: HO-0305
==============================================================================
ADJUSTER NOTES:
Claim no. 2024-61907, [CLAIMANT_NAME], HO-0305 ed. 03-24. Coverage A $350,000. Hurricane Helene, NHC-named, damaged roof on Sept 26 2024. Roof inspection report from March 2023 in the file already documents lifted shingles and a damaged ridge cap on the north slope. Contractor estimate $19,500 for the full roof, of which about $4,000 is the north slope.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0305
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 15, 2024
Title: Increased Deductible for Named Storm Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE AND SCOPE
This endorsement sets a separate, higher deductible that applies only to loss
caused by a Named Storm as defined below. Every other covered peril continues
to be settled under the standard policy deductible.

CLAUSE NS-1 — NAMED STORM DEFINITION
A "Named Storm" means a tropical cyclone, hurricane, or tropical storm that has
been assigned a name by the National Hurricane Center (NHC) or the equivalent
national meteorological authority at any point during its lifecycle, regardless
of whether the storm bore a name at the time it caused loss to the described
premises.

CLAUSE NS-2 — NAMED STORM DEDUCTIBLE
When a Named Storm causes or contributes to a covered loss, the Named Storm
Deductible is $5,000 or 2% of the Coverage A limit, whichever is greater.
This deductible applies per occurrence, not per storm season.

CLAUSE NS-3 — STACKING PROHIBITION
The Named Storm Deductible under this endorsement replaces — and does not stack
with — any all-peril deductible stated on the declarations page. The higher
of the two deductibles applies.

CLAUSE NS-4 — TRIGGER WINDOW
The Named Storm Deductible attaches from the time the NHC issues a watch or
warning for the county of the described premises until 72 hours after the
final advisory for that storm is published.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0305 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-20 | Temporary repairs not documented           | Emergency repairs claimed without photographs or invoices          |
| E-21 | Losses below Named Storm deductible        | Total damage under the Named Storm deductible is not payable       |
| E-22 | Coastal storm surge classified as flood    | Surge loss falls to NFIP and is not covered by this form           |
| E-23 | Pre-existing wind damage                   | Damage already present before the Named Storm made landfall        |
| E-24 | Business property in dwelling              | Commercial inventory or equipment kept on the premises             |

SECTION III — DEDUCTIBLE SCHEDULE
Policy Year 2024 Named Storm Deductible: $5,000 minimum or 2% of Cov-A.
For a dwelling insured at $300,000: deductible = $6,000.
For a dwelling insured at $200,000: deductible = $5,000 (floor applies).

SECTION IV — EFFECTIVE DATE
This endorsement is effective March 15, 2024.
Premium adjustment: $0.00 (deductible shift, no additional premium).

END OF ENDORSEMENT HO-0305 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-61907  

DATE OF LOSS: 26 September 2024  

POLICY FORMS: HO-0305 (ed. 03‑24)  

LOSS SUMMARY:  
The insured’s roof was damaged by Hurricane Helene, a named storm, resulting in lifted shingles and a damaged ridge cap on the north slope. A contractor has estimated the total roof repair cost at $19,500, of which approximately $4,000 pertains to the north‑slope damage.  

DEDUCTIBLE:  
Named Storm deductible applies – the greater of $5,000 or 2 % of the Coverage A limit ($350,000 × 2 % = $7,000). Therefore the deductible is $7,000.  
[SOURCE: HO-0305_sa_chunk_004 | HO-0305 | CLAUSE-NS-2]  

COVERAGE POSITION:  
The loss is caused by a Named Storm, which triggers the Named Storm deductible under the policy. However, the provided endorsement excerpts do not contain the specific coverage language that defines what is covered under Coverage A (dwelling) or how roof repairs are payable. Consequently, the coverage position for the roof repair cost is **undetermined** based on the available policy text.  

EXCLUSIONS APPLIED:  
None identified in the provided endorsement excerpts.  

OPEN ITEMS:  
- Full contractor invoice for the roof repair (to confirm final cost).  
- Proof of loss documentation (e.g., signed claim form, photographs of damage).  
- Confirmation that the loss was reported within any applicable reporting timeframes (if required by other policy provisions).
==============================================================================
```

```
==============================================================================
SUMMARY 21/25   case s06   policy forms: HO-0304
==============================================================================
ADJUSTER NOTES:
Claim #2024-34419. Insured [CLAIMANT_NAME], HO-0304 ed. 03-24, ded $1,000. Copper supply line to the laundry burst on 29 June 2024 while insured was away. Insured discovered it on return 1 July and reported it to us on 6 July (five days after discovery). Plumber's report: pipe split along a seam, a single sudden failure, no evidence of prior leakage; drywall behind was dry before the split. Damage estimate $11,800.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-34419  
DATE OF LOSS: 29 June 2024  
POLICY FORMS: HO-0304 (ed. 03‑24)  
LOSS SUMMARY: A copper supply line serving the laundry burst suddenly on 29 June 2024 while the insured was away. The insured discovered the loss on 1 July, reported it on 6 July (five days after discovery), and the plumber’s report confirms a single, abrupt failure with no prior leakage; the adjacent drywall was dry. Estimated damage is $11,800.  
DEDUCTIBLE: $1,000 (as noted in the policy endorsement)  
COVERAGE POSITION: The water loss meets the definition of a “sudden and accidental” discharge under CLAUSE‑WD‑1, which provides coverage for such events [SOURCE: HO-0304_sa_chunk_003 | HO-0304 | CLAUSE-WD-1]. However, the loss was not reported within the required 72‑hour window after discovery; the report was made five days later. SECTION‑III requires reporting within 72 hours, and a failure to do so may result in the loss being re‑classified as gradual seepage and denied under E‑11 [SOURCE: HO-0304_sa_chunk_008 | HO-0304 | SECTION-III]. Consequently, coverage is denied based on the untimely report.  
EXCLUSIONS APPLIED: Late reporting exclusion – loss reported after 72 hours, triggering potential re‑classification as gradual seepage and denial per SECTION‑III.  
OPEN ITEMS:  
- Confirmation of the exact time of discovery and the time the report was submitted (to verify the 72‑hour window).  
- Documentation of any emergency mitigation actions taken and associated costs (to assess applicability of CLAUSE‑WD‑3).  
- Any additional damages or losses (e.g., mold) that may arise and require separate evaluation.
==============================================================================
```

```
==============================================================================
SUMMARY 22/25   case s13   policy forms: HO-0304, HO-0308
==============================================================================
ADJUSTER NOTES:
clm 2024-59977, [CLAIMANT_NAME], HO-0304 ed. 03-24 + HO-0308 ed. 05-24, ded $1,000. Earthquake 2 Sept 2024 shifted the house; the kitchen supply line ruptured at the wall and flooded the ground floor. Water damage estimate $14,000. Insured says a burst supply line is covered under her water endorsement.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0308
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 1, 2024
Title: Earth Movement Exclusion — Broadened Definition Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement widens the earth movement exclusion in the base homeowners
policy and removes the ambiguity that has driven disputed determinations on
sinkholes, soil subsidence, and expansive soil claims.

CLAUSE EM-1 — EARTH MOVEMENT DEFINED (BROADENED)
For purposes of this endorsement, "earth movement" means any movement,
shifting, rising, sinking, settling, or destabilizing of the earth or soil,
including but not limited to:
  (a) Earthquake, including tremors, aftershocks, and volcanic eruption;
  (b) Landslide, mudslide, or debris flow;
  (c) Sinkhole formation or collapse;
  (d) Soil subsidence or expansive soil events;
  (e) Man-made earth movement, including mining-induced subsidence.

CLAUSE EM-2 — CONCURRENT CAUSATION RULE
If earth movement and a covered peril act concurrently or in sequence to
produce a loss, the entire loss is excluded under this endorsement.
Coverage does not attach to any portion of the loss attributable to
the covered peril when earth movement is also a contributing cause.

CLAUSE EM-3 — ENSUING FIRE EXCEPTION
Notwithstanding CLAUSE EM-1 and EM-2, if earth movement causes a fire,
coverage for the ensuing fire damage is not excluded by this endorsement.

CLAUSE EM-4 — ENGINEERING REPORT
Where the Company obtains a geotechnical or structural engineering report on
a claimed loss, that report is the controlling evidence of whether earth
movement contributed to the damage.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0308 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-31 | Earth movement — all forms                 | Earthquake, landslide, mudslide, sinkhole, subsidence; all forms   |
|      |                                            | of earth movement as defined in CLAUSE EM-1 are excluded.          |
|      |                                            | Concurrent cause rule applies (CLAUSE EM-2).                       |
| E-32 | Man-made earth movement                    | Mining subsidence, excavation-induced movement, compaction failure |
| E-33 | Sinkhole collapse damage                   | Structural damage from sinkhole formation or sudden collapse       |
| E-34 | Expansive soil and shrinkage               | Foundation cracking from soil expansion, shrinkage, or settlement  |
| E-35 | Mudslide and debris flow                   | Flowing earth, mud, or debris whatever set it in motion            |

SECTION III — ENSUING LOSS EXCEPTION NOTE
Ensuing fire under CLAUSE EM-3 is the only exception to this exclusion.
Water damage that follows from pipes ruptured by earth movement stays
excluded under E-31 through the concurrent cause rule in CLAUSE EM-2.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0308 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024-59977  
DATE OF LOSS: 02 Sep 2024  
POLICY FORMS: HO-0304 (Water Damage Limitations and Supply Line Coverage Endorsement), HO-0308 (Ensuing Loss Exception Endorsement)  
LOSS SUMMARY: An earthquake on 2 September 2024 shifted the insured’s house, causing the kitchen water‑supply line to rupture at the wall and flood the ground floor. The estimated water‑damage loss is $14,000.  
DEDUCTIBLE: $1,000 (as noted by the adjuster)  
COVERAGE POSITION: The water damage is **not covered**. While HO‑0304’s exclusion table states that a burst interior supply line is **not excluded** and is covered under the water‑damage clauses (E‑17) [SOURCE: HO-0304_sa_chunk_007 | HO-0304 | EXCLUSION-TABLE], HO‑0308 expressly excludes water damage that follows from pipes ruptured by earth movement, referencing exclusion E‑31 and the concurrent cause rule in CLAUSE EM‑2 [SOURCE: HO-0308_sa_chunk_009 | HO-0308 | CLAUSE-EM-3]. The specific cause—earthquake‑induced rupture—triggers the HO‑0308 exclusion, overriding the general coverage for burst lines.  
EXCLUSIONS APPLIED: E‑31 (Water damage from pipes ruptured by earth movement) – applied via HO‑0308 [SOURCE: HO-0308_sa_chunk_009 | HO-0308 | CLAUSE-EM-3]  
OPEN ITEMS:  
- Confirmation of the exact policy endorsement version and any additional clauses that might affect the concurrent cause analysis.  
- Verification of the cause of rupture (earth movement vs. other factors) through engineering or inspection reports.  
- Any additional documentation required to substantiate the loss estimate.
==============================================================================
```

```
==============================================================================
SUMMARY 23/25   case s25   policy forms: HO-0308
==============================================================================
ADJUSTER NOTES:
CLM 2024 59490. HO-0308. ded $1,000. Quake 5 Aug 2024 cracked the chimney; the fireplace was lit and the crack let fire into the roof space. Fire damage $27,000, chimney/structural cracking $9,000.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0308
Edition Date: 05-24
Policy Line: homeowners
Effective Date: May 1, 2024
Title: Earth Movement Exclusion — Broadened Definition Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement widens the earth movement exclusion in the base homeowners
policy and removes the ambiguity that has driven disputed determinations on
sinkholes, soil subsidence, and expansive soil claims.

CLAUSE EM-1 — EARTH MOVEMENT DEFINED (BROADENED)
For purposes of this endorsement, "earth movement" means any movement,
shifting, rising, sinking, settling, or destabilizing of the earth or soil,
including but not limited to:
  (a) Earthquake, including tremors, aftershocks, and volcanic eruption;
  (b) Landslide, mudslide, or debris flow;
  (c) Sinkhole formation or collapse;
  (d) Soil subsidence or expansive soil events;
  (e) Man-made earth movement, including mining-induced subsidence.

CLAUSE EM-2 — CONCURRENT CAUSATION RULE
If earth movement and a covered peril act concurrently or in sequence to
produce a loss, the entire loss is excluded under this endorsement.
Coverage does not attach to any portion of the loss attributable to
the covered peril when earth movement is also a contributing cause.

CLAUSE EM-3 — ENSUING FIRE EXCEPTION
Notwithstanding CLAUSE EM-1 and EM-2, if earth movement causes a fire,
coverage for the ensuing fire damage is not excluded by this endorsement.

CLAUSE EM-4 — ENGINEERING REPORT
Where the Company obtains a geotechnical or structural engineering report on
a claimed loss, that report is the controlling evidence of whether earth
movement contributed to the damage.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0308 ed. 05-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-31 | Earth movement — all forms                 | Earthquake, landslide, mudslide, sinkhole, subsidence; all forms   |
|      |                                            | of earth movement as defined in CLAUSE EM-1 are excluded.          |
|      |                                            | Concurrent cause rule applies (CLAUSE EM-2).                       |
| E-32 | Man-made earth movement                    | Mining subsidence, excavation-induced movement, compaction failure |
| E-33 | Sinkhole collapse damage                   | Structural damage from sinkhole formation or sudden collapse       |
| E-34 | Expansive soil and shrinkage               | Foundation cracking from soil expansion, shrinkage, or settlement  |
| E-35 | Mudslide and debris flow                   | Flowing earth, mud, or debris whatever set it in motion            |

SECTION III — ENSUING LOSS EXCEPTION NOTE
Ensuing fire under CLAUSE EM-3 is the only exception to this exclusion.
Water damage that follows from pipes ruptured by earth movement stays
excluded under E-31 through the concurrent cause rule in CLAUSE EM-2.

SECTION IV — EFFECTIVE DATE
This endorsement is effective May 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement).

END OF ENDORSEMENT HO-0308 ed. 05-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: CLM 2024 59490  
DATE OF LOSS: 05 Aug 2024  
POLICY FORMS: HO-0308  

LOSS SUMMARY: An earthquake on 5 August 2024 cracked the chimney of the insured dwelling. The fireplace was lit, and the crack allowed fire to spread into the roof space, resulting in $27,000 of fire damage and $9,000 of chimney/structural cracking.  

DEDUCTIBLE: $1,000 (as noted by the adjuster).  

COVERAGE POSITION:  
- The fire damage ($27,000) is covered because the loss is an “ensuing fire” caused by earth movement, which is expressly excepted from the fire exclusion in the endorsement. [SOURCE: HO-0308_sa_chunk_005 | HO-0308 | CLAUSE-EM-3] [SOURCE: HO-0308_sa_chunk_009 | HO-0308 | CLAUSE-EM-3]  
- Coverage for the chimney and structural cracking ($9,000) cannot be determined from the provided endorsement excerpts; no specific clause addressing earthquake‑induced structural damage is present.  

EXCLUSIONS APPLIED:  
- Water damage that follows from earth‑movement‑caused pipe rupture is excluded, but no such water damage is reported in this loss. [SOURCE: HO-0308_sa_chunk_009 | HO-0308 | CLAUSE-EM-3]  

OPEN ITEMS:  
1. Engineering/structural report confirming the extent of chimney and building damage and its direct link to the earthquake.  
2. Fire investigation report verifying that the fire originated from the cracked chimney caused by the quake.  
3. Determination of whether the $9,000 structural damage falls under a covered peril under any other clause of the policy.  
4. Confirmation of the applicable deductible for this type of loss (the endorsement excerpts do not specify a deductible for earthquake‑related fire).
==============================================================================
```

```
==============================================================================
SUMMARY 24/25   case s02   policy forms: HO-0304, HO-0306
==============================================================================
ADJUSTER NOTES:
clm 2024 40271 / [CLAIMANT_NAME] / forms HO-0304 03-24 + HO-0306 04-24, ded $1,000. Supply line to upstairs toilet burst 7/8/24, reported next morning. Mold found behind drywall two weeks later. Licensed remediation contractor estimate on file, $7,400. Insured also submitted an $850 invoice from an air quality testing lab and wants both paid.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

HOMEOWNERS ENDORSEMENT
Form Number: HO-0306
Edition Date: 04-24
Policy Line: homeowners
Effective Date: April 1, 2024
Title: Mold, Fungi, and Wet Rot Exclusion Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PURPOSE
This endorsement settles how the policy treats mold, fungi, wet rot, dry rot,
and bacteria, whether those conditions follow a covered water loss or arise on
their own. It narrows the base wording rather than adding to it.

CLAUSE MF-1 — MOLD AND FUNGI EXCLUSION (GENERAL)
We do not cover loss caused directly or indirectly by mold, fungi, wet rot,
dry rot, or bacteria. This exclusion applies regardless of whether the mold
or fungi results from a covered or uncovered water event.

CLAUSE MF-2 — REMEDIATION SUBLIMIT EXCEPTION
Notwithstanding CLAUSE MF-1, if mold is a direct result of a covered sudden
and accidental water discharge event (as defined in form HO-0304 ed. 03-24,
CLAUSE WD-1), we will pay up to $10,000 for mold remediation costs, provided:
  (a) The water event is reported within 72 hours of discovery, and
  (b) A licensed remediation contractor provides a written estimate.

CLAUSE MF-3 — TESTING EXCLUSION
We do not cover the cost of air quality testing, mold sampling, or laboratory
analysis, even if the underlying remediation is covered under CLAUSE MF-2.

CLAUSE MF-4 — SUBLIMIT IS NOT ADDITIONAL INSURANCE
The $10,000 remediation sublimit is part of, and not in addition to, the
Coverage A limit. Payment under MF-2 reduces the amount available for the
underlying water loss.

SECTION II — EXCLUSIONS TABLE
EXCLUSION TABLE — HO-0306 ed. 04-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-22 | Mold damage — general                      | All mold-related losses UNLESS remediation sublimit applies        |
| E-23 | Fungi and wet rot losses                   | Wet rot, dry rot, or fungi in any form, whatever the water source  |
| E-24 | Bacteria contamination                     | Loss attributable to bacterial growth or contamination             |
| E-25 | Mold testing and air sampling costs        | Lab, air-quality, and surface sampling charges are not payable     |
| E-26 | Pre-existing mold at time of policy issue  | Mold present anywhere in the dwelling before policy inception      |
| E-27 | Mold from HVAC condensation (chronic)      | Condensation mold where the HVAC system is 3+ years unserviced     |

SECTION III — CONDITIONS
Nothing in this endorsement widens coverage beyond what it states outright.
Where this endorsement and the base policy disagree on a mold or fungi loss,
this endorsement governs.

SECTION IV — EFFECTIVE DATE
This endorsement is effective April 1, 2024.
Premium adjustment: $0.00 (exclusion endorsement, no additional premium).

END OF ENDORSEMENT HO-0306 ed. 04-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024 40271  
DATE OF LOSS: 07/08/2024 (burst supply line to upstairs toilet)  
POLICY FORMS: HO-0304 03‑24, HO-0306 04‑24  
LOSS SUMMARY: On 7/8/24 the insured’s water supply line to the upstairs toilet burst and was reported the following morning. Two weeks later mold was discovered behind drywall; a licensed remediation contractor submitted a $7,400 estimate, and the insured also submitted an $850 air‑quality testing invoice.  
DEDUCTIBLE: $1,000  

COVERAGE POSITION:  
- Mold remediation costs are covered up to $10,000 under Clause WD‑1 of HO‑0306, provided the water event is reported within 72 hours of discovery and a licensed contractor estimate is on file. Both conditions are satisfied (report within 24 hours, estimate provided) → $7,400 remediation claim is covered.  
- After applying the $1,000 deductible, the payable amount for remediation is $6,400.  
- The $850 air‑quality testing invoice is excluded under the “Mold testing and air sampling costs” exclusion (Code E‑25).  

EXCLUSIONS APPLIED:  
- Code E‑25 – Mold testing and air sampling costs are not payable. [SOURCE: HO-0306_sa_chunk_009 | HO-0306 | EXCLUSION‑TABLE]  

OPEN ITEMS:  
1. Confirmation of coverage for the underlying water‑supply line damage under HO‑0304 (no specific coverage language provided in the excerpts).  
2. Verification that the mold discovered two weeks after the burst is causally linked to the reported water event (required to satisfy the “remediation sub‑limit” exception to the general mold exclusion).  
3. Any additional documentation required to confirm the timely reporting of the water event (within 72 hours).
==============================================================================
```

```
==============================================================================
SUMMARY 25/25   case s22   policy forms: HO-0304
==============================================================================
ADJUSTER NOTES:
clm 2024 35590 - [CLAIMANT_NAME] - HO-0304 ed. 03-24 - ded $1,000. Kitchen sink supply line burst 30 July 2024, reported the same afternoon. Insured shut the valve and rented dehumidifiers ($640 invoice). Floor and cabinet damage estimate $7,900.

--- POLICY WORDING -----------------------------------------------------------
HOMEOWNERS ENDORSEMENT
Form Number: HO-0304
Edition Date: 03-24
Policy Line: homeowners
Effective Date: March 1, 2024
Title: Water Damage Limitations and Supply Line Coverage Endorsement

This endorsement modifies insurance provided under the:
HOMEOWNERS POLICY — SPECIAL FORM

SECTION I — PROPERTY COVERAGES

COVERAGE A — DWELLING
This endorsement replaces the base policy treatment of water losses that
originate inside the dwelling, including supply lines, drain lines, and the
plumbing infrastructure serving the described premises.

CLAUSE WD-1 — SUDDEN AND ACCIDENTAL DISCHARGE
Coverage applies to sudden and accidental discharge or overflow of water or
steam from within a plumbing, heating, air conditioning, or automatic fire
protective sprinkler system, or from within a household appliance. The term
"sudden and accidental" means an event that is abrupt, unintended, and
not the result of continuous seepage or leakage over a period of time exceeding
fourteen (14) consecutive days.

CLAUSE WD-2 — SUPPLY LINE DEFINITION
A "supply line" means any pipe or tube that carries potable water under pressure
from the main service entry or from a distribution manifold to any plumbing
fixture, appliance, or point of use within or attached to the described dwelling.

CLAUSE WD-3 — MITIGATION DUTY
Following a water loss, the insured must take reasonable steps to stop the
source and dry affected materials. Reasonable emergency mitigation costs are
payable under Coverage A and are not subject to a separate deductible.

SECTION II — EXCLUSIONS TABLE
The rows below govern water losses under this endorsement. Each row states the
exclusion code, the peril, and the conditions under which the row operates.

EXCLUSION TABLE — HO-0304 ed. 03-24

| Code | Excluded Peril                             | Conditions / Scope                                                 |
|------|--------------------------------------------|--------------------------------------------------------------------|
| E-10 | Unoccupied dwelling freeze loss            | Freeze damage where heat was not maintained and water not shut off |
| E-11 | Gradual seepage or leakage                 | Water seeping or leaking continuously beyond the 14-day WD-1 limit |
| E-12 | Flood from external surface water          | Surface water entering from outside — storm surge, runoff, overflow|
| E-13 | Sewer or drain backup (off-premises)       | Backup originating in a municipal or shared drain line             |
| E-14 | Ground water intrusion                     | Subsurface water reaching the foundation, slab, or basement        |
| E-15 | Ice dam damage without maintenance record  | Ice dam loss where no annual roof inspection record exists         |
| E-16 | Appliance wear-and-tear overflow           | Overflow from an appliance past 15 years of service, unserviced    |
| E-17 | Burst supply line — NOT excluded           | Water damage from a sudden burst of an interior supply line IS     |
|      |                                            | COVERED under CLAUSE WD-1 and WD-2; this row confirms coverage     |
|      |                                            | is NOT withheld under this endorsement for that specific peril.    |
| E-18 | Intentional discharge                      | Any water release brought about deliberately by an insured person  |

SECTION III — CONDITIONS
A water loss under this endorsement must be reported within 72 hours of the
insured first discovering it. A report made outside that window may be
reclassified as gradual seepage and denied under E-11.

SECTION IV — EFFECTIVE DATE AND SUPERSESSION
This endorsement is effective March 1, 2024, and supersedes any conflicting
language in the base homeowners policy regarding water supply line coverage.
Premium adjustment: $24.00 additional annual premium.

END OF ENDORSEMENT HO-0304 ed. 03-24

--- OUTPUT TO GRADE ----------------------------------------------------------
CLAIM NUMBER: 2024 35590  
DATE OF LOSS: July 30, 2024  
POLICY FORMS: HO-0304 – Water Damage Limitations and Supply Line Coverage Endorsement; HO-0305 – Deductible Schedule (referencing the base HOMEOWNERS POLICY — SPECIAL FORM)  

LOSS SUMMARY: On July 30, 2024 the kitchen‑sink supply line burst. The insured shut the valve, rented dehumidifiers (invoice $640), and reported floor and cabinet damage with an estimate of $7,900.  

DEDUCTIBLE: The policy deductible is a minimum of $5,000 (or $6,000 for a $300,000 dwelling) as set out in the deductible schedule. [SOURCE: HO-0305_sa_chunk_009 | HO-0305 | SECTION-III]  

COVERAGE POSITION: The burst pipe is a “supply line” as defined in the endorsement, so water damage resulting from the burst is covered under the HO-0304 endorsement, subject to the applicable deductible. [SOURCE: HO-0304_sa_chunk_004 | HO-0304 | CLAUSE-WD-2]  

EXCLUSIONS APPLIED: No exclusions in the provided endorsement language directly apply to this loss.  

OPEN ITEMS: • Obtain final contractor estimate for floor and cabinet repairs.  
• Confirm payment of the $5,000 (or applicable) deductible.  
• Retain the dehumidifier rental invoice and any additional documentation required by the policy.
==============================================================================
```

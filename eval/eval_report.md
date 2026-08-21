# LeaseOwl v2 evaluation: detector vs expert labels

Model: `gemini-3.6-flash`  ·  Items scored: 147

## Headline

- Exact 3-way accuracy: **90/147 = 61.2%**
- Cohen's kappa (model vs human): **0.44** (agreement beyond chance; >0.6 substantial, >0.8 near-perfect)

## Problem detection (deficient or missing = flagged)

- Precision: 64.0%  (of items the model flags, how many the expert also flagged)
- Recall: 96.4%  (of items the expert flagged, how many the model caught)
- False-flag rate: 70.3%  (of items the expert judged fine, how many the model wrongly flagged)
- TP 80 · FP 45 · FN 3 · TN 19

## Accuracy by importance

| Importance | Accuracy |
|---|---|
| CRITICAL | 3/7 = 43% |
| HIGH | 55/91 = 60% |
| MEDIUM | 27/42 = 64% |
| VARIABLE | 5/7 = 71% |

## Confusion matrix (rows = expert, cols = model)

| expert \ model | present | deficient | missing |
|---|---|---|---|
| present | 19 | 43 | 2 |
| deficient | 3 | 21 | 8 |
| missing | 0 | 1 | 50 |

## Disagreements (for error analysis)

| TA | item | expert | model | model reason |
|---|---|---|---|---|
| TA1.pdf | 7 | deficient | missing | The agreement does not contain any clause addressing air-conditioner servicing o |
| TA1.pdf | 15 | deficient | missing | The agreement does not mention tenant responsibility for utilities (water, elect |
| TA1.pdf | 18 | deficient | missing | The agreement does not outline any process or mechanism (such as mediation or ar |
| TA2.pdf | 6 | present | deficient | The agreement includes a $200 repair threshold but fails to state that the tenan |
| TA2.pdf | 7 | deficient | missing | The agreement does not contain any clause addressing air-conditioner maintenance |
| TA2.pdf | 10 | present | deficient | Clause 4.6 prohibits subletting without written consent but fails to explicitly  |
| TA2.pdf | 11 | present | deficient | Clause 4.4 addresses pets and requires landlord consent, but fails to specify th |
| TA2.pdf | 15 | present | deficient | Clause 4.3 specifies that the tenant is responsible for utility bills but fails  |
| TA2.pdf | 19 | deficient | present | The agreement specifies conditions for early termination by the landlord, includ |
| TA3.pdf | 1 | deficient | missing | The agreement does not contain any provisions regarding HDB approval, compliance |
| TA3.pdf | 2 | present | deficient | The preamble addresses the lease term but lacks exact start and end dates and fa |
| TA3.pdf | 4 | present | deficient | The agreement specifies the deposit amount and deduction conditions, but fails t |
| TA3.pdf | 6 | present | deficient | Clause 11 sets a minor repair threshold of S$200 but fails to specify that the t |
| TA3.pdf | 7 | present | deficient | Clause 13 states that the landlord will provide air conditioner servicing every  |
| TA3.pdf | 10 | present | deficient | Clause 9 prohibits subletting without the landlord's permission, but fails to re |
| TA3.pdf | 14 | present | deficient | Clause 13 addresses tenant move-out condition and disposal, but fails to include |
| TA3.pdf | 15 | present | deficient | Clause 5 addresses utilities but states rent includes water, electricity, and ga |
| TA3.pdf | 17 | present | deficient | Clause 8 addresses alterations but fails to specify written consent from the lan |
| TA4.pdf | 1 | missing | deficient | Clause 7 addresses pass and document verification for legal stay, but the agreem |
| TA4.pdf | 2 | present | deficient | The preamble addresses the lease duration but uses unfulfilled blank placeholder |
| TA4.pdf | 5 | deficient | present | Clause 6 defines a defect-free period of seven days from the date of handover du |
| TA4.pdf | 10 | present | deficient | Clause 10 prohibits subletting without the landlord's written consent, but fails |
| TA4.pdf | 11 | present | deficient | Clause 18 addresses pets and requires written landlord consent, but fails to req |
| TA4.pdf | 12 | deficient | missing | The agreement explicitly prohibits early termination and does not include a dipl |
| TA4.pdf | 14 | present | deficient | Clause 13 specifies handover condition and general cleaning upon move-out, but f |
| TA4.pdf | 15 | present | deficient | Clause 5 addresses utilities but states rent includes water, electricity, and Wi |
| TA4.pdf | 17 | present | deficient | Clause 8 prohibits alterations without permission, but omits the requirement for |
| TA5.pdf | 2 | present | deficient | Clause 2 addresses the lease period but fails to provide exact start and end dat |
| TA5.pdf | 4 | present | deficient | Clause 4 states the deposit amount, deduction conditions, and prohibition agains |
| TA5.pdf | 10 | present | deficient | Clause 8 explicitly prohibits subletting without the landlord's written consent, |
| TA5.pdf | 14 | present | deficient | While the agreement addresses yielding up the room in good condition and returni |
| TA5.pdf | 19 | deficient | present | The agreement specifies conditions for landlord early termination upon tenant br |
| TA5.pdf | 20 | present | deficient | While Clause 13(1) states that no visitors are allowed, it fails to explicitly m |
| TA6.pdf | 1 | deficient | missing | The agreement is for a private condominium unit and contains no provisions regar |
| TA6.pdf | 3 | present | deficient | The agreement specifies the payment due date and method, but leaves the monthly  |
| TA6.pdf | 7 | present | deficient | Clause 1(k) places the cost of quarterly air-conditioning servicing on the Landl |
| TA6.pdf | 10 | present | deficient | Clause 1(p) prohibits subletting without the landlord's written consent, but fai |
| TA6.pdf | 11 | present | deficient | Clause 1(u) addresses pets and requires landlord consent, but fails to state tha |
| TA6.pdf | 12 | present | missing | The agreement does not contain a diplomatic or break clause specifying early ter |
| TA6.pdf | 13 | present | deficient | The agreement includes an Inventory List, but fails to require a Property Condit |
| TA6.pdf | 14 | present | deficient | The agreement addresses move-out condition in Clause 1(w), but fails to specify  |
| TA6.pdf | 15 | present | deficient | The agreement addresses utilities by including them in the rent up to a cap with |
| TA6.pdf | 16 | present | missing | The agreement does not require the tenant to maintain renter's insurance or cove |
| TA6.pdf | 17 | present | deficient | Clause 1(m) addresses unauthorized alterations and requires the landlord's prior |
| TA6.pdf | 20 | present | deficient | The agreement addresses overnight guests but fails to specify the permitted numb |
| TA7.pdf | 1 | deficient | missing | The agreement does not contain any provisions regarding HDB approval, compliance |
| TA7.pdf | 2 | present | deficient | Clause 1 specifies the commencement date and term duration of 24 months, but fai |
| TA7.pdf | 7 | present | deficient | Clause 2(j) addresses quarterly air-conditioner servicing but places the expense |
| TA7.pdf | 8 | present | deficient | Clauses 2(m)–(o) address access for repairs and viewings by prior appointment, b |
| TA7.pdf | 10 | present | deficient | Clause 2(p) prohibits subletting without the landlord's written consent but fail |
| TA7.pdf | 11 | present | deficient | The clause addresses pets and requires landlord consent, but fails to state that |
| TA7.pdf | 13 | present | deficient | The agreement references an attached Inventory List, but fails to require a Prop |
| TA7.pdf | 14 | present | deficient | The agreement specifies move-out condition, professional curtain cleaning, and k |
| TA7.pdf | 15 | present | deficient | Clause 2(c) covers payment for water, electricity, gas, and telephone, but fails |
| TA7.pdf | 16 | present | deficient | Clause 2(u) requires the tenant to insure personal chattels against loss or dama |
| TA7.pdf | 17 | present | deficient | The agreement restricts alterations without the landlord's written consent but f |
| TA7.pdf | 21 | present | deficient | Clause 5(m) specifies that the agreement is governed by Singapore law, but fails |
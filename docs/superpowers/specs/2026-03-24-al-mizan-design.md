# Al-Mizan (الميزان) — The Evidence Balance

*"And He established the balance, that you not transgress within the balance."* — 55:7-8

## 1. Problem

Patients continue to be enrolled in trials testing questions where cumulative evidence already provides a clear answer. The CRASH-2 trial randomized 10,000 patients to steroids for head injury after meta-analytic evidence already showed harm. This is a preventable ethical failure caused by the absence of real-time evidence monitoring.

## 2. Goal

Build the world's first browser-based evidence equipoise monitor that determines, for any treatment comparison, whether the balance of evidence has tipped — and if so, when, and how many patients were randomized after that point.

## 3. Target

- **Primary:** BMJ Evidence-Based Medicine (research tool + case study)
- **Secondary:** Annals of Internal Medicine (commentary on research waste)
- **Location:** `C:\AlMizan\al-mizan.html`

## 4. Architecture

Single-file HTML app (established pattern). 4 tabs. No server dependency.

### Tab 1: Data Input
- Manual entry: study name, year, effect (OR/RR/HR/MD), CI or SE, n_exp, n_ctrl
- CSV import (paste or file upload)
- Built-in exemplar datasets:
  - **Steroids for head injury** (CRASH-2 context, ~10 trials, clear harm signal)
  - **Tranexamic acid for bleeding** (~8 trials, benefit emerged mid-timeline)
  - **Intensive glucose control in ICU** (NICE-SUGAR context, ~7 trials, harm signal)
- Data table: editable, sortable by year, delete rows

### Tab 2: The Balance (الميزان) — Main Visualization
- **Cumulative meta-analysis forest plot**: vertical timeline, each row = the pooled estimate after adding that study chronologically
- **TSA monitoring boundaries**: O'Brien-Fleming alpha-spending overlaid on cumulative Z-statistic
  - Inner wedge = futility boundary
  - Outer wedge = efficacy boundary
  - When the Z-curve crosses the boundary → the balance has tipped
- **The Tipping Point**: highlighted with a marker — the exact study/year where the boundary was crossed
- **Traffic light verdict**: MIZAN-RED / MIZAN-AMBER / MIZAN-GREEN
- **Fragility ribbon**: at each timepoint, show how many studies would need to change to flip (color intensity)

### Tab 3: The Waste (الإسراف)
- **Post-tipping trials**: list of all studies that enrolled patients AFTER the tipping point
- **Total patients randomized after tipping**: the headline "waste" number
- **Cumulative waste curve**: patients over time, with the tipping point marked
- **Cost estimate**: optional, patients × estimated per-patient trial cost
- **Counter-factual**: "If monitoring had been in place, [N] patients could have been spared"

### Tab 4: Report & Export
- Auto-generated methods text
- Summary table: tipping point year, verdict, waste count, RIS
- R code export (equivalent meta::metacum + rpact TSA)
- Print-ready layout
- Copy buttons

## 5. Core Engine

### 5.1 Cumulative Meta-Analysis
For studies ordered chronologically (by year, then alphabetically):
- At each step k (k = 1, ..., K), compute DL random-effects pooled estimate from studies 1..k
- Store: theta_k, se_k, ci_lo_k, ci_hi_k, p_k, tau2_k, I2_k, Z_k

### 5.2 Trial Sequential Analysis (TSA)
Based on the Wetterslev-Thorlund-Gluud framework (Copenhagen Trial Unit):

**Required Information Size (RIS):**
- For ratio outcomes: RIS = 4 × (z_alpha + z_beta)^2 / (ln(RR_target))^2
- For continuous: RIS = 4 × sigma^2 × (z_alpha + z_beta)^2 / delta^2
- Adjusted for heterogeneity: RIS_adj = RIS × (1 + D^2) where D^2 = I^2/(1-I^2)

**Monitoring boundaries (O'Brien-Fleming alpha-spending):**
- Information fraction at step k: t_k = n_cumulative_k / RIS_adj
- Alpha-spending: same OBF function from AdaptSim
- Z-boundaries computed via the same recursive algorithm

**Crossing detection:**
- At each step, check if |Z_k| > z_boundary_k (efficacy) or inside futility wedge
- The first crossing = the tipping point

### 5.3 Fragility at Each Timepoint
At each cumulative step k:
- Compute the leave-one-out: for each study i ≤ k, what is the pooled estimate without study i?
- Count how many LOO removals flip the significance → that's the fragility count
- A review with fragility = 0 means removing ANY single study flips the conclusion

### 5.4 Verdict Classification
- **MIZAN-RED**: Z-curve has crossed the efficacy monitoring boundary (balance tipped)
- **MIZAN-AMBER**: Information fraction > 50% of RIS AND current p < 0.05, but boundary not yet crossed
- **MIZAN-GREEN**: Information fraction < 50% of RIS OR current p ≥ 0.05

### 5.5 Waste Calculation
- Identify the tipping point: study k* where Z first crosses the boundary
- Sum all patients (n_exp + n_ctrl) from studies k*+1 to K
- This is the "post-tipping enrollment" — the human cost of not monitoring

## 6. Built-in Datasets

### Steroids for Head Injury (paradigmatic example)
~10 RCTs from 1970s-2004 culminating in CRASH (2004, n=10,008).
Expected: tipping point around 1997 (after ~5 trials showing harm trend), CRASH enrolled 10,008 patients after.

### Tranexamic Acid for Trauma Bleeding
~8 RCTs. CRASH-2 (2010) was the landmark. Expected: balance tips at CRASH-2 itself (first large trial).

### Intensive Glucose Control in ICU
Van den Berghe (2001) showed benefit, but NICE-SUGAR (2009, n=6,104) showed harm. Expected: tipping point shifts — first tips toward benefit, then reverses.

## 7. Validation

1. Cross-validate cumulative MA against R's `meta::metacum()` on all 3 exemplars
2. TSA boundaries verified against Copenhagen TSA software (published boundary tables)
3. Fragility counts verified by manual computation on small (k=5) datasets
4. Selenium tests: 25+ covering all tabs, edge cases (k=1, all studies same direction, no tipping point)

## 8. Success Criteria

1. Cumulative MA matches R meta::metacum within ±0.001
2. TSA boundaries match Copenhagen tables within ±0.05 Z-units
3. Waste calculation correctly identifies post-tipping studies
4. All 3 exemplar datasets produce clinically meaningful verdicts
5. Traffic light verdict is deterministic and reproducible

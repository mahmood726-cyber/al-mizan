# Al-Mizan: An Evidence Equipoise Monitor for Detecting When the Balance of Evidence Has Tipped

## Authors
Mahmood Ahmad^1

^1 Royal Free Hospital, London, UK

Corresponding author: mahmood.ahmad2@nhs.net

---

## Abstract

**Background:** Patients continue to be enrolled in clinical trials testing questions where cumulative evidence already provides a clear answer. Trial Sequential Analysis (TSA) can detect when sufficient evidence has accrued, but no accessible tool exists to monitor evidence equipoise in real time and quantify the human cost of delayed recognition.

**Methods:** We developed Al-Mizan, an open-access browser-based evidence equipoise monitor that combines cumulative meta-analysis, Trial Sequential Analysis with O'Brien-Fleming alpha-spending boundaries, leave-one-out fragility assessment, and post-tipping waste quantification. We demonstrate the tool on three clinical exemplars: corticosteroids for traumatic brain injury, tranexamic acid for bleeding, and intensive glucose control in ICU.

**Results:** For corticosteroids in head injury, the cumulative Z-statistic showed no benefit accumulating across 8 trials (1976-1995). The landmark CRASH trial (2004, n=10,008) confirmed harm (RR 1.05, 95% CI 1.01-1.10), but the TSA monitoring boundary was not crossed before CRASH, illustrating that equipoise persisted until the definitive trial. For intensive glucose control, the cumulative evidence initially favoured treatment (Van den Berghe 2001) but reversed with NICE-SUGAR (2009, n=6,022), demonstrating a "reversal tipping point." The tool classified each scenario with a traffic-light verdict (MIZAN-RED: balance tipped; MIZAN-AMBER: trend emerging; MIZAN-GREEN: equipoise remains) and quantified post-tipping enrollment where applicable.

**Conclusions:** Al-Mizan provides real-time evidence equipoise monitoring with waste quantification, enabling researchers, ethics committees, and data safety monitoring boards to assess whether a new trial is justified. The tool is freely available as a browser application requiring no installation.

---

## Introduction

The ethical principle of clinical equipoise requires that there be genuine uncertainty about which treatment is superior before a randomised trial can be justified [1]. Yet this principle is routinely violated — not through malice, but through the absence of systematic evidence monitoring. Chalmers [2] documented that thousands of patients have been enrolled in trials testing questions where cumulative meta-analytic evidence already pointed clearly in one direction.

The most striking example is the CRASH trial of corticosteroids for traumatic brain injury [3]. When CRASH randomised 10,008 patients in 2004, a cumulative meta-analysis of preceding trials showed no convincing benefit and a trend toward harm. Similar concerns have been raised about intensive glucose control in ICU [4], where the initial positive signal from Van den Berghe (2001) was followed by NICE-SUGAR (2009) showing harm — a "reversal" that earlier monitoring might have anticipated.

Trial Sequential Analysis (TSA), developed by the Copenhagen Trial Unit [5,6], addresses this by applying group-sequential monitoring boundaries to cumulative meta-analysis. When the cumulative Z-statistic crosses the monitoring boundary, sufficient evidence has accrued to declare the question answered. However, the existing TSA software is desktop-only Java, handles one meta-analysis at a time, and does not quantify the human cost of delayed recognition.

We present Al-Mizan (Arabic for "the balance"), a browser-based evidence equipoise monitor that combines cumulative meta-analysis, TSA, fragility assessment, and waste quantification in a single accessible tool. Al-Mizan addresses three questions for any treatment comparison: (1) Has the balance of evidence tipped? (2) When did it tip? (3) How many patients were randomised after the tipping point?

## Methods

### Tool architecture

Al-Mizan is a single-file HTML application (~2,600 lines) requiring no installation, server, or internet connection. It runs entirely in the user's web browser and is validated by 30 automated Selenium tests.

### Cumulative meta-analysis

Studies are ordered chronologically by publication year. At each step k, a DerSimonian-Laird random-effects meta-analysis is computed on studies 1 through k, yielding the pooled effect estimate (theta_k), its standard error, 95% confidence interval, I-squared heterogeneity, and the cumulative Z-statistic (Z_k = theta_k / SE_k).

### Trial Sequential Analysis

For ratio measures (RR, OR, HR), the Required Information Size (RIS) is computed using the event-rate-aware formula:

RIS = 2 x [z_{alpha/2} x sqrt(2 x p_bar x (1 - p_bar)) + z_beta x sqrt(p_c x (1 - p_c) + p_e x (1 - p_e))]^2 / (p_c - p_e)^2

where p_c is the estimated control-arm event rate, p_e = p_c x RR_target, and p_bar = (p_c + p_e)/2 [5]. This is adjusted for heterogeneity by multiplying by (1 + D^2) where D^2 = I^2/(1 - I^2). A default control-arm event rate of 0.20 is used when individual arm event counts are unavailable, which is conservative for most mortality and morbidity outcomes.

O'Brien-Fleming alpha-spending monitoring boundaries are computed using the Lan-DeMets spending function alpha*(t) = 2 - 2 x Phi(z_{alpha/2} / sqrt(t)) [7], with boundary z_k = z_{alpha/2} / sqrt(t_k) at each cumulative step where t_k = N_cumulative / RIS.

### Fragility assessment

At each cumulative step (k >= 2), leave-one-out analysis determines how many individual study removals would flip the statistical significance of the pooled estimate. A fragility count of 0 means the conclusion is robust to any single study removal; higher counts indicate greater sensitivity. The fragility index is undefined for k=1 (a single study).

### Verdict classification

- **MIZAN-RED**: The cumulative Z-statistic has crossed the O'Brien-Fleming monitoring boundary. The balance has tipped.
- **MIZAN-AMBER**: Information fraction exceeds 50% of RIS and current p < 0.05, but the boundary has not been crossed. A trend is emerging.
- **MIZAN-GREEN**: Information fraction below 50% or p >= 0.05. Genuine equipoise remains.

### Waste quantification

When a tipping point is detected, Al-Mizan identifies all studies published after the tipping point and sums their total enrollment. This "post-tipping enrollment" represents patients who were randomised to a question where the balance had already tipped.

### Exemplar datasets

Three clinical scenarios were pre-loaded:

1. **Corticosteroids for traumatic brain injury** (9 RCTs, 1976-2004): The paradigmatic example of evidence waste, culminating in CRASH (n=10,008).
2. **Tranexamic acid for trauma bleeding** (3 RCTs, 2010-2020): CRASH-2, WOMAN, HALT-IT — a benefit signal emerging from a landmark trial.
3. **Intensive glucose control in ICU** (7 RCTs, 2001-2010): Van den Berghe showed benefit, then NICE-SUGAR showed harm — an evidence reversal.

## Results

### Corticosteroids for traumatic brain injury

Across 8 pre-CRASH trials (1976-1995), the cumulative pooled RR ranged from 0.75 to 1.02, with wide confidence intervals consistently crossing 1.0. The TSA monitoring boundary was not crossed at any point before CRASH. Upon adding CRASH (2004), the pooled RR moved to 1.05 (95% CI 1.01-1.10), and with sufficient information accrued, the Z-statistic approached the boundary. **Verdict: MIZAN-AMBER to MIZAN-RED** depending on the target RR setting. The key finding is that equipoise was genuinely maintained until CRASH — the earlier trials were too small to resolve the question.

### Tranexamic acid for trauma bleeding

CRASH-2 (2010) was the first large trial and immediately produced a significant result (RR 0.91, 95% CI 0.85-0.97). The Z-statistic crossed the monitoring boundary at this first large data point. **Verdict: MIZAN-RED** after CRASH-2. WOMAN (2017) and HALT-IT (2020) enrolled a combined 32,000 additional patients — however, HALT-IT tested a different population (GI bleeding), so the "waste" calculation requires clinical judgment about whether these are the same question.

### Intensive glucose control in ICU

Van den Berghe (2001) showed a strong benefit (RR 0.58). Subsequent trials diluted this signal toward the null. NICE-SUGAR (2009) tipped the evidence toward harm (cumulative RR crossing 1.0). This "reversal" pattern — where early evidence favors treatment but later evidence reverses — is particularly important for monitoring: early MIZAN-RED (benefit) transitions through MIZAN-GREEN (equipoise re-established) to a new MIZAN-RED (harm).

## Discussion

Al-Mizan operationalises the concept of evidence equipoise monitoring in an accessible browser tool. Three features distinguish it from existing approaches:

First, **waste quantification** gives a concrete human cost to delayed evidence synthesis. When a DSMB or ethics committee asks "should this trial continue?", Al-Mizan provides not just a statistical answer but a patient count.

Second, the **traffic-light verdict** translates complex statistical output into an actionable classification. MIZAN-RED means "the balance has tipped — further trials require strong justification." MIZAN-GREEN means "equipoise remains — trials are ethically appropriate."

Third, **fragility tracking** at each cumulative step reveals how stable the emerging conclusion is. A MIZAN-RED verdict with high fragility (many LOO flips) warrants more caution than one with zero fragility.

### Limitations

1. TSA boundaries assume a fixed target effect size, which must be specified a priori. Different targets produce different boundaries and potentially different verdicts.
2. The RIS computation uses a default control-arm event rate of 20% when individual arm event counts are unavailable. For outcomes with very different baseline rates, users should interpret the RIS as approximate.
3. The tool uses published aggregated data, not individual patient data. Real-time monitoring during an ongoing trial would require access to interim data.
4. The "waste" calculation is retrospective — it identifies patients who *were* randomised after the tipping point, not patients who *will be*.
5. Clinical judgment is essential: statistical tipping does not automatically render further research unethical, particularly when testing different populations, doses, or outcomes.

### Implications

Al-Mizan could be used by: (1) ethics committees evaluating whether a proposed trial is justified given existing evidence; (2) data safety monitoring boards assessing whether cumulative external evidence warrants early stopping; (3) funding agencies deciding whether to invest in a new trial; and (4) systematic reviewers presenting the temporal evolution of evidence.

## Conclusions

Al-Mizan provides a freely accessible tool for monitoring evidence equipoise, detecting tipping points, and quantifying the human cost of continued randomisation after the balance has tipped. The tool demonstrates that the concept of "evidence waste" can be made concrete and measurable, supporting more ethical allocation of research resources.

## Data availability

The tool is available at https://github.com/mahmood726-cyber/al-mizan. All built-in datasets use published trial-level data from Cochrane reviews.

## Funding

No external funding was received for this work.

## Competing interests

The authors declare no competing interests.

## Patient and public involvement

No patients or members of the public were involved in the design of this tool.

## References

1. Freedman B. Equipoise and the ethics of clinical research. N Engl J Med. 1987;317(3):141-145.
2. Chalmers I. The lethal consequences of failing to make use of all relevant evidence about the effects of medical treatments. J R Soc Med. 2006;99(7):341-345.
3. CRASH Trial Collaborators. Effect of intravenous corticosteroids on death within 14 days in 10,008 adults with clinically significant head injury. Lancet. 2004;364(9442):1321-1328.
4. NICE-SUGAR Study Investigators. Intensive versus conventional glucose control in critically ill patients. N Engl J Med. 2009;360(13):1283-1297.
5. Wetterslev J, Thorlund K, Brok J, Gluud C. Trial sequential analysis may establish when firm evidence is reached in cumulative meta-analysis. J Clin Epidemiol. 2008;61(1):64-75.
6. Thorlund K, Engstrom J, Wetterslev J, Brok J, Imberger G, Gluud C. User manual for Trial Sequential Analysis (TSA). Copenhagen Trial Unit; 2011.
7. Lan KKG, DeMets DL. Discrete sequential boundaries for clinical trials. Biometrika. 1983;70(3):659-663.

# Decoding Customer Value: A SQL-Driven Retention Strategy
**Consulting & Analytics Club, IIT Guwahati | Summer Projects '26** 

---

## Project Overview
This repository contains an end-to-end customer intelligence framework built for a direct-to-consumer (D2C) fashion brand to transition from reactive, discount-driven operations to data-backed retention strategy. By analyzing 3,900 customers across 18 behavioral and transactional variables using Python, SQL, and Power BI, we engineered bespoke loyalty metrics, isolated high-value segments, and constructed a multi-phase promotional sunset playbook to protect margins without sacrificing sales volume.

---

## Repository Structure
* `Dataset.csv` - Raw, unprocessed direct-to-consumer transactional and behavioral dataset.
* `dataset_engineered.csv` - Cleaned and processed dataset containing engineered metrics such as dependency scores, value tiers, and satisfaction flags.
* `phase1.py` - Python script managing data preparation, missing value treatment, and feature engineering logic.
* `phase2.py` - Structured SQL query layer containing segmentation logic answering the brand's core business performance questions.
* `customer_intelligence_dashboard.pbix` - Four-panel Power BI interactive dashboard optimized for non-technical founding teams.
  - **Panel 1 - Customer Pyramid:** Value tier distribution (High/Mid/Low) across the 3,900-customer base
  - **Panel 2 - Promo Dependency Funnel:** Retention rate plotted by segment; who needs discounts vs. who doesn't
  - **Panel 3 - Geographic Opportunity Map:** States ranked by spend and organic loyalty rate to surface untapped markets
  - **Panel 4 - Category Funnel:** Product categories by purchase history, showing entry-point vs. retention categories
* `playbook.md` - Actionable retention playbook detailing the strategic promo sunset plan and data-backed ideal customer profile.
* `executive_summary.md` - A concise, one-page business briefing distilling the critical insights, financial exposures, and tactical timelines for senior leadership.

---

## Tools Used
* **Python (Pandas, NumPy):** Missing data handling, outlier detection, and analytical feature engineering.
* **MySQL:** Structured query layer, database design, customer segmentation, and behavioral trend indexing.
* **Power BI:** Data modeling, DAX engineering, and a four-panel visual interface mapping value distribution, category funnels, and geographic demand.

---

## Methodology Note - Dual Loyalty Definitions

Two competing definitions of customer loyalty were constructed and tested:

- **Definition A (Threshold-Based):** A customer was classified as loyal if their `Previous Purchases` count exceeded the dataset median (25). This captured tenure but failed to distinguish between customers who returned organically versus those who returned only under discount incentives. Correlation with revenue was weak.

- **Definition B (Behavioral Composite - Adopted):** A customer was classified as loyal if they met all three conditions: no promo code used, not discount-applied, AND previous purchases above median. This definition isolates *intrinsic* loyalty - customers who return and spend without needing a price incentive. It showed stronger correlation with higher average spend (+$8.65) and was grounded in observable behavioral signals rather than tenure alone.

`Loyal_DefB` is used throughout all segmentation, SQL queries, and dashboard logic.

---

## Key Findings
* **The Promotional Leakage Core:** 43% of the active customer portfolio consists of discount hunters who drain margin and spend an average of $9 less per transaction than organically loyal buyers.
* **High-Tier Cannibalization:** Over 90% of High Value Tier customers are already intrinsically loyal to the brand, yet 41% to 47% of their transactions are being dilute by unnecessary discount exposure.
* **Untapped Regional Traction:** Arizona and Tennessee stand out as premium growth pockets, maintaining organic brand loyalty rates above 35% and promotional dependency scores below 37%.

---

## Dataset
[View Dataset](https://drive.google.com/file/d/1aJUEgbqHj-Rp4KPh2TRe8MtSMcHZ8Lqk/view)


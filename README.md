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
* `playbook.md` - Actionable retention playbook detailing the strategic promo sunset plan and data-backed ideal customer profile.
* `executive_summary.md` - A concise, one-page business briefing distilling the critical insights, financial exposures, and tactical timelines for senior leadership.

---

## Key Findings
* **The Promotional Leakage Core:** 43% of the active customer portfolio consists of discount hunters who drain margin and spend an average of $9 less per transaction than organically loyal buyers.
* **High-Tier Cannibalization:** Over 90% of High Value Tier customers are already intrinsically loyal to the brand, yet 41% to 47% of their transactions are being dilute by unnecessary discount exposure.
* **Untapped Regional Traction:** Arizona and Tennessee stand out as premium growth pockets, maintaining organic brand loyalty rates above 35% and promotional dependency scores below 37%.

---

## Tools Used
* **Python (Pandas, NumPy):** Missing data handling, outlier detection, and analytical feature engineering.
* **MySQL:** Structured query layer, database design, customer segmentation, and behavioral trend indexing.
* **Power BI:** Data modeling, DAX engineering, and a four-panel visual interface mapping value distribution, category funnels, and geographic demand.

# AI Challenge: Vita Sicura Context

## Challenge Overview

The core objective of this AI Challenge is to apply techniques such as **Machine Learning, Generative AI, and Business Intelligence** to solve strategic problems faced by **Vita Sicura S.p.A.**, a fictional, historic, leading Italian insurance company. The company aims to sustain long-term profitability by focusing on two main goals: consolidating its customer base through loyalty, and achieving growth within the high-value **upper-retail/affluent** client segment.

Key strategic priorities for 2026 include:

*   **Product Mix Rebalance:** Shifting focus toward new **multi-branch (multiramo)** products (those with high financial content) and strengthening the **P&C (Danni)** segment, particularly Home and Health/Accident insurance.
*   **Capture Multi-holding Clients:** Incrementing the number of clients who hold multiple policies via targeted cross-selling strategies.

The challenge is organized into four innovation streams designed to support strategic decisions and enhance distribution networks.

## Primary Innovation Streams

The four streams outlining possible intervention areas for the Data Science & AI team are:

1.  **Customer DNA (Conoscere il Cliente):** Focuses on **segmenting the customer base** to identify emerging personas and high-value clusters.
2.  **Visione aumentata (Pricing Intelligente e Potenziale Territoriale):** Focuses on leveraging external data (satellite and Street View images) via **Computer Vision** to enrich models for **pricing and risk scoring** (specifically for Home products), and identifying areas with high commercial potential (i.e., protection gaps).
3.  **Next Best Move (AI per Azioni Commerciali Mirate):** Focuses on developing **predictive models** for cross-selling (to increase multi-polizza clients) and retention (anti-churn), culminating in suggested **Next Best Actions** for insurance consultants.
4.  **Competitive Edge (Ottimizzare l’offerta Danni):** Focuses on analyzing the profitability of the P&C portfolio, performing competitor **benchmarking**, and identifying pricing adjustments based on technical indicators like **loss ratio**.

## Data Dictionary

The challenge utilizes seven synthetic datasets, all provided as CSV files:

| File Name | Records | Description |
| :--- | :--- | :--- |
| `clienti.csv` | 11,200 | Client data (active and non-active), including demographics, scoring, Customer Lifetime Value (CLV), and marketing details. |
| `polizze.csv` | 18,039 | Policy details (active and historic), including premiums, sums insured, commissions, and margins. |
| `sinistri.csv` | 16,839 | Claim records (losses), detailing amounts requested/liquidated, causes, and management status. |
| `reclami.csv` | 16,839 | Complaint records, covering type, severity, status, and resolution times. |
| `abitazioni.csv` | 5,190 | Home/dwelling information, including address, floor area (`metratura`), and alarm system. |
| `interazioni_clienti.csv` | 41,195 | Marketing interactions data, specifying channels, outcomes, response clusters, and conversion flags. |
| `competitor_prodotti.csv` | 12 | Data on competitor products with reference premiums for price benchmarking. |
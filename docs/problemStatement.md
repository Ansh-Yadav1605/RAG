# Mutual Fund FAQ Assistant — Facts-Only Q&A

## Overview

The objective of this project is to build a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as **AMC** (Asset Management Company) websites, **AMFI**, and **SEBI**.

The system must **strictly avoid** providing investment advice, opinions, or recommendations. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

---

## Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)**-based assistant that:

- Answers **factual queries** about mutual fund schemes
- Uses a **curated corpus** of official documents
- Provides **concise, source-backed** responses

---

## Target Users

- Retail investors comparing mutual fund schemes
- Customer support and content teams handling repetitive mutual fund queries

---

## Scope of Work

### 1. Corpus Definition

#### Selected AMC

**HDFC Mutual Fund** (HDFC Asset Management Company Limited)

#### Selected Schemes (5)

| # | Scheme Name | Category | Groww URL |
|---|-------------|----------|-----------|
| 1 | HDFC Large Cap Fund – Direct Plan – Growth | Large Cap | [Link](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
| 2 | HDFC Mid-Cap Opportunities Fund – Direct Plan – Growth | Mid Cap | [Link](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| 3 | HDFC Small Cap Fund – Direct Plan – Growth | Small Cap | [Link](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth) |
| 4 | HDFC Gold ETF Fund of Fund – Direct Plan – Growth | Gold ETF FoF | [Link](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth) |
| 5 | HDFC Silver ETF Fund of Fund – Direct Plan – Growth | Silver ETF FoF | [Link](https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth) |

#### Corpus URLs (Primary Data Sources)

| # | Source | URL |
|---|--------|-----|
| 1 | HDFC Large Cap Fund – Groww | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 2 | HDFC Mid-Cap Opportunities Fund – Groww | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |
| 3 | HDFC Small Cap Fund – Groww | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 4 | HDFC Gold ETF Fund of Fund – Groww | https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth |
| 5 | HDFC Silver ETF Fund of Fund – Groww | https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth |

> [!NOTE]
> These Groww scheme pages serve as the primary corpus. Each page contains key facts such as expense ratio, exit load, minimum SIP/lump-sum amounts, riskometer classification, benchmark index, fund manager details, and scheme category — covering the full scope of facts-only queries the assistant must handle.

### 2. FAQ Assistant Requirements

The assistant must:

- Answer **facts-only queries**, such as:
  - Expense ratio of a scheme
  - Exit load details
  - Minimum SIP amount
  - ELSS lock-in period
  - Riskometer classification
  - Benchmark index
  - Process to download statements or capital gains reports

- Ensure:
  - Each response is limited to a **maximum of 3 sentences**
  - Each response includes **exactly one citation link**
  - Each response includes a footer:

    > *"Last updated from sources: \<date\>"*

### 3. Refusal Handling

The assistant must **refuse** non-factual or advisory queries, such as:

- *"Should I invest in this fund?"*
- *"Which fund is better?"*

Refusal responses should:

- Be polite and clearly worded
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

### 4. User Interface (Minimal)

The solution should include a simple interface with:

- A **welcome message**
- **Three example questions**
- A visible **disclaimer**:

  > *"Facts-only. No investment advice."*

---

## Constraints

### Data and Sources

- Use **only** official public sources (AMC, AMFI, SEBI)
- Do **not** use third-party blogs or aggregator websites

### Privacy and Security

- Do **not** collect, store, or process:
  - PAN or Aadhaar numbers
  - Account numbers
  - OTPs
  - Email addresses or phone numbers

### Content Restrictions

- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance-related queries, provide a **link to the official factsheet only**

### Transparency

- Responses must be short, factual, and verifiable
- Every answer must include a **source link** and **last updated date**

---

## Expected Deliverables

### README Document

- Setup instructions
- Selected AMC and schemes
- Architecture overview (RAG approach)
- Known limitations

### Disclaimer Snippet

> *"Facts-only. No investment advice."*

---

## Success Criteria

| # | Criterion |
|---|-----------|
| 1 | Accurate retrieval of factual mutual fund information |
| 2 | Strict adherence to facts-only responses |
| 3 | Consistent inclusion of valid source citations |
| 4 | Proper refusal of advisory queries |
| 5 | Clean, minimal, and user-friendly interface |

---

## Summary

The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only verified, source-backed financial information, without any advisory bias or speculative content.

# Imara

**Financial reconciliation made simpler.**

Imara is a lightweight reconciliation tool for small businesses, Saccos, NGOs, and teams that manually compare financial records from different sources.

It takes two transaction datasets for example, an M-Pesa export and an internal ledger cleans the data, compares the records, and highlights transactions that do not match.

> **Goal:** turn a slow, repetitive spreadsheet task into a clear and repeatable process.

---

## The Problem

Financial records often come from different systems and rarely look exactly the same.

A person may have to manually compare:

* M-Pesa or bank statements
* Internal ledgers
* Excel spreadsheets
* CSV exports
* Payment records

This can make it difficult to quickly find:

* Missing transactions
* Amount differences
* Date differences
* Invalid or incomplete records
* Other inconsistencies between two sources

Imara is being built to help with that first layer of reconciliation.

---

## What Imara Does

The project is being built in small stages.

### Current focus

**1. Clean**

Turn messy transaction data into a consistent structure.

**2. Match**

Compare two cleaned datasets and identify differences.

**3. Report**

Present the results in a way that a non-technical person can understand.

The first version intentionally avoids unnecessary complexity. It does not require AI, blockchain, government integrations, or a large cloud infrastructure.

---

## Current Status

**Stage:** Month 1 — Core Engine
**Current focus:** Week 1 — The Cleaner
**Status:** 🚧 In active development

The first milestone is to build a reliable data-cleaning layer that can:

* Read transaction data
* Handle common date and amount formats
* Recognize different column names
* Reject invalid records safely
* Explain why a record was rejected
* Produce predictable, structured transaction records
* Be tested against messy data

The cleaner must work reliably before the matching system is built.

---

## Planned MVP

```text
              IMARA
                │
        ┌───────┴────────┐
        │                │
   Financial File A  Financial File B
        │                │
        └───────┬────────┘
                ↓
             CLEAN
                ↓
             MATCH
                ↓
            IDENTIFY
           DIFFERENCES
                ↓
             REPORT
```

The initial MVP will focus on one organization and one reconciliation workflow at a time.

---

## Technology

The initial MVP is intentionally simple:

* **Python** — core application logic
* **Pandas** — data processing
* **Streamlit** — web interface
* **SQLite** — lightweight local storage
* **ReportLab** — PDF reports
* **pytest** — automated testing
* **Git + GitHub** — version control

Additional infrastructure will only be introduced when the product actually needs it.

---

## Project Principles

Imara is being developed around a few simple principles:

**Build small.**
Solve the core problem before adding features.

**Use real data.**
Real files and real workflows are more valuable than impressive synthetic demos.

**Fail clearly.**
A bad record should produce an understandable explanation, not a silent failure.

**Test everything important.**
Changes should not quietly break functionality that already works.

**Talk to users.**
Product decisions should come from real reconciliation problems, not assumptions.

**Security matters.**
Financial data must be handled carefully even while the project is still an MVP.

---

## What Imara Is Not

The first version is deliberately **not**:

* An accounting system
* An auditing replacement
* A fraud-detection system
* An AI financial advisor
* A KRA/eTIMS integration
* A SASRA integration
* A banking or M-Pesa API
* A full enterprise financial platform

Those may be considered in the future only if there is a genuine need for them.

---

## Roadmap

### Month 1 — Core Engine

* [ ] Week 1: Cleaner
* [ ] Week 2: Matcher
* [ ] Week 3: Real-data testing
* [ ] Week 4: First human-readable report

### Month 2 — Usable MVP

* [ ] Streamlit interface
* [ ] PDF reports
* [ ] Feedback-driven improvements
* [ ] Real user demonstrations

### Month 3 — Reliability

* [ ] Persistent storage
* [ ] Basic organization separation
* [ ] Larger-file testing
* [ ] Full internal test pass

### Month 4 — Pilot

* [ ] Deploy
* [ ] Approach potential users
* [ ] Run a real pilot
* [ ] Collect the real-world fix list

### Month 5 — Version 1.0

* [ ] Fix pilot problems
* [ ] Polish the product
* [ ] Add a simple payment process
* [ ] Documentation
* [ ] Release Imara v1.0

---

## Repository Structure

The project will grow gradually. The structure will change as the product develops.

```text
imara/
├── engine/
├── tests/
├── data/
├── app/
├── reports/
├── docs/
├── README.md
└── requirements.txt
```

The structure should follow the product as it grows rather than being designed around features we do not need yet.

---

## Development Philosophy

Imara is being built as a real product, not just as a demonstration project.

The objective is simple:

> **Find a real reconciliation problem, build the smallest useful solution, put it in front of real people, learn from how they use it, and improve it.**

---

**Status:** 🚧 Building
**Version:** 0.1.0 — early development

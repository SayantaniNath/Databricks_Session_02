# Sayantani — DE Learning Plan

Target: AI Data Engineer, SF Bay Area — Apply-ready by Oct 2026  |  1 hr/day  |  Last updated: 2026-06-05

## Progress Snapshot

Stage| Status| Target  
---|---|---  
Stage 1 — Kaggle Python| ✅ Complete| May 21 (done early)  
Stage 2 — Kaggle Pandas| ✅ Complete| Jun 4 (done May 26)  
Stage 2B — PySpark + Spark + Databricks| 🟡 In Progress| Jun 4–18  
AWS Cloud Practitioner (Maarek)| 🟡 In Progress| Mid-late Jun  
Stage 3 — Redis + Kafka| ⏳ Not Started| Jun 18 – Jul 2  
Stage 4 — Airflow| ⏳ Not Started| Jul 2–16  
Stage 5 — GraphQL| ⏳ Not Started| Jul 16–23  
Stage 6 — DeepLearning.AI LLM Foundations| ⏳ Not Started| Jul 23 – Aug 6  
Stage 6.5 — System Design (4 phases)| 🟡 Phase A (Ch 1–3 done)| Now → Oct 15  
Stage 7 — RAG Pipelines| ⏳ Not Started| Aug 6–20  
Stage 8 — Agentic Workflows| ⏳ Not Started| Aug 20 – Sep 3  
Stage 9 — Portfolio Polish| ⏳ Not Started| Oct 15–31  
GCP / Vertex AI Track| ⏳ Not Started| Parallel w/ Stages 6–8  
Databricks DEA Cert| ⏳ Not Started| ~Aug 2026  
Databricks Academy (ongoing)| ⏳ Not Started| Ongoing  
dbt| ⏳ Not Started| Ongoing  
Interview Prep (SQL + NeetCode Python)| 🟡 In Progress| Ongoing  
  
## Weekly Schedule

Day| Focus  
---|---  
Monday| Stage 2B — PySpark / Spark / Databricks (1 hr)  
Tuesday| AWS / DEA (1 hr) + DataLemur (~20 min)  
Wednesday| Stage 2B — PySpark / Spark / Databricks (1 hr)  
Thursday| AWS / DEA (1 hr) + DDIA reading (~30–45 min)  
Friday| Stage 2B (1 hr) + light SD sketch (~30 min, from Jun 14)  
Saturday| Opportunistic only — no commitment  
Sunday| Rest  
  
## Stage 1 — Kaggle Python

Kaggle Python Course✅ CompleteTarget: May 21, 2026 (finished early)

  * Lesson 1 — Variables, Data Types, Print
  * Lesson 2 — Functions and Getting Help
  * Lesson 3 — Booleans and Conditionals
  * Lesson 4 — Lists
  * Lesson 5 — Loops and List Comprehensions
  * Lesson 6 — Strings and Dictionaries
  * Lesson 7 — Working with External Libraries



## Stage 2 — Kaggle Pandas

Kaggle Pandas Course✅ CompleteTarget: Jun 4, 2026 (finished May 26 — 9 days early)

  * Lesson 1 — Creating, Reading and Writing (2026-05-18)
  * Lesson 2 — Indexing, Selecting & Assigning (2026-05-20) — 5/5 from-blank
  * Lesson 3 — Summary Functions and Maps (2026-05-25) — 8/8 from-blank
  * Lesson 4 — Grouping and Sorting (2026-05-25) — 9/9 from-blank
  * Lesson 5 — Data Types and Missing Values (2026-05-26) — 13/13 from-blank
  * Lesson 6 — Renaming and Combining (2026-05-26) — 8/8 from-blank



All lessons taught in-chat using FinFlow data, not Kaggle's official notebooks. Practice files in `finflow/practice_pandas_lesson*.py`.

## Stage 2B — PySpark + Spark Internals + Data Modeling + Databricks Boosters

PySpark + Databricks🟡 In ProgressTarget: Jun 4–18, 2026

  * Spark architecture deep-dive (2026-05-28) — Driver/Executors, DAG, narrow vs wide, broadcast joins. Doc: `Spark_Architecture_Walkthrough.html`
  * DataFrame API Lessons 1 & 2 (2026-05-29) — 12/12 from-blank. Spark UI live at localhost:4040.
  * PySpark SQL — Lesson 3 (2026-06-02) — SQL + DF API side-by-side, Catalyst plan confirmed identical. `practice_pyspark_lesson3.py`
  * Spark on Databricks — CE workspace 
    * Lakeflow Designer intro (2026-05-21, Andreas Kretz)
    * First live CE session (2026-06-03) — serverless compute, Unity Catalog volume, display() vs show()
  * FinFlow integration — process JSONL with Spark instead of Pandas
  * Spark internals — AQE, skew, caching, partitioning deep-dive
  * Data modeling — star/snowflake, SCDs Type 1/2/3, grain definition
  * ⭐ Delta Lake mechanics — time travel, MERGE, OPTIMIZE+Z-ORDER, VACUUM, transaction log
  * ⭐ Structured Streaming — watermarks, exactly-once, checkpoints, trigger modes
  * ⭐ Delta Live Tables (DLT) — declarative pipelines, expectations
  * ⭐ Unity Catalog basics — three-level namespace, metastore, lineage, grants
  * Skew + AQE deep-dive — diagnose with Spark UI, salting
  * Open Lakehouse Formats — Delta vs Iceberg vs Hudi (~30 min)



⚠️ Local env: Python 3.14 + PySpark 3.5.8 — `createDataFrame([list])` broken. Use `spark.read.json()` from files instead.

## AWS Cloud Practitioner (CLF-C02)

Maarek (Udemy) + Tutorials Dojo🟡 In ProgressTarget: Mid-late Jun 2026

  * Skilljar Modules 1–5 (complete)
  * Skilljar Module 6+ — SKIPPED, replaced by Maarek
  * Maarek "Ultimate AWS CCP CLF-C02" — through IAM (incl. policies hands-on) as of 2026-05-29
  * Tutorials Dojo Round 1 — full timed exam, review wrong answers (~3 hrs)
  * Patch weak topics from TD gaps (~2 hrs)
  * Tutorials Dojo Round 2 — score 80%+ → book real exam (~3 hrs)



## Stage 3 — Redis + Kafka Practicals

Redis + Kafka⏳ Not StartedTarget: Jun 18 – Jul 2, 2026

  * Redis commands + Python redis library
  * Kafka topics, producers, consumers + Python kafka-python
  * ⭐ Real-Time Fraud Detection Pipeline (capstone) — Kafka → IsolationForest scoring → Delta Lake → Airflow. Data: PaySim synthetic transactions.



## Stage 4 — Airflow

Apache Airflow⏳ Not StartedTarget: Jul 2–16, 2026

  * DAGs, operators, scheduling, local install



## Stage 5 — GraphQL

GraphQL⏳ Not StartedTarget: Jul 16–23, 2026

  * Queries, mutations, schema, playground practice



## Stage 6 — DeepLearning.AI LLM Foundations

LLM + LangChain + Responsible AI⏳ Not StartedTarget: Jul 23 – Aug 6, 2026

  * LangChain for LLM Application Development
  * AI Agents in LangGraph
  * ChatGPT Prompt Engineering for Developers
  * Building Systems with ChatGPT API
  * Vertex AI Gemini API basics
  * Responsible / Ethical AI Practices (~2 hrs)



## Stage 6.5 — System Design (FAANG-grade, 4 phases)

Phase A — DDIA Reading🟡 In ProgressNow → Jun 14, 2026

  * DDIA Ch 1 (done by 2026-05-29)
  * DDIA Ch 2 — Data Models and Query Languages (done by 2026-05-29)
  * DDIA Ch 3 — Storage and Retrieval (done 2026-06-01, via YouTube)
  * DDIA Ch 4 — Encoding and Evolution (Jun 13–14 weekend)



### Bonus Case Studies (done early)

  * 2026-06-01 — Prepaid Credits system (Chargebee-style). Steps 1–5 full. Doc: `SystemDesign_Prepaid_Credits_Walkthrough.html`
  * 2026-06-03 — Design LeetCode (NeetCode SD). All 7 SLA points covered. Notes: `interview_prep/sd_qa_log.md`



Phase B — DDIA + Structured Case Studies⏳ Not StartedJun 14 → Aug 31, 2026

1 DDIA chapter + 1 case study per weekend. 6-step framework: requirements → estimation → API → schema → HLD → deep-dive.

  * 60% DE-flavored: streaming pipeline, lakehouse/medallion, CDC, schema evolution
  * 30% classic product: Meta feed, URL shortener, chat
  * 10% ML/AI: feature store, RAG, recommender
  * ⭐ 3 Databricks-flavored: Delta Lake protocol, Unity Catalog, feature store on Databricks



Phase C — Out-loud Mocks + Behavioral⏳ Not StartedSep 1 → Oct 15, 2026

2 mocks/week. Excalidraw + verbal walkthrough, recorded. Build behavioral story bank in parallel.

Phase D — Portfolio + Apply⏳ Not StartedOct 15 → Oct 31, 2026

Portfolio polish + start applying. Apply-ready by Oct 15.

## Stage 7 — RAG Pipelines

RAG + Vector DBs⏳ Not StartedTarget: Aug 6–20, 2026

  * LangChain RAG, Chroma vector DB, Resume Q&A; Bot project
  * Vertex AI Vector Search — GCP-native, compare with Chroma



## Stage 8 — Agentic Workflows

LangGraph + CrewAI + Databricks Capstone⏳ Not StartedTarget: Aug 20 – Sep 3, 2026

  * LangGraph, CrewAI — AI Job Application Agent project
  * Vertex AI Agent Builder
  * ⭐ Databricks Lakehouse + AI Data Quality Monitor (capstone) — Bronze→Silver→Gold medallion, Delta Lake, Unity Catalog, Claude API anomaly detection agent, Airflow DAG. Blueprint: `Project_Databricks_Lakehouse_Blueprint.html`



## Stage 9 — Portfolio Polish

GitHub Portfolio⏳ Not StartedTarget: Oct 15–31, 2026

  * 4 projects: FinFlow, Fraud Detection Pipeline, Databricks Lakehouse + AI Monitor, AI Job Agent
  * READMEs, architecture diagrams, deploy/run instructions, screenshots



## Parallel / Ongoing Tracks

GCP / Vertex AI⏳ Not StartedParallel with Stages 6–8

  * Vertex AI Workbench, Model Garden, Vector Search, Agent Builder



Databricks DEA Cert⏳ Not Started~Aug 2026

  * Databricks Academy — "Data Engineering with Databricks" path
  * Derar Alhussein Udemy course (~6 hrs)
  * Practice exams — official + Skillcertpro



Databricks Academy (ongoing)⏳ Not Started

  * Generative AI Fundamentals, Apache Spark Programming



dbt (ongoing)⏳ Not Started

  * dbt Fundamentals, dbt + Snowflake ELT Patterns



## Interview Prep (Parallel Ongoing)

NeetCode Python + SQL + System Design🟡 In Progress

### NeetCode 150 — 3 patterns only

  * Two Sum (Arrays & Hashing) — 2026-06-03, solved with hints. Log: `interview_prep/python_log.md`
  * Contains Duplicate
  * Valid Anagram, Group Anagrams, Top K Frequent
  * Two Pointers: Valid Palindrome, 3Sum
  * Sliding Window: Best Time to Buy Stock, Longest Substring Without Repeating



### SQL

  * Window functions deep-dive — NTILE, PERCENT_RANK (2026-05-27, dailysql.com)
  * DataLemur — weekend sessions



### System Design Case Studies

  * Prepaid Credits (2026-06-01)
  * Design LeetCode — SLA deep-dive (2026-06-03)



Last updated: 2026-06-05  |  Source of truth: Claude Code memory (project_learning_progress.md)

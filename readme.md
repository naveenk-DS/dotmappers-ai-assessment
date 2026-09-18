# End-to-End AI Support Ticket Analytics System

## AI Engineer Technical Assessment — DOTMappers IT Pvt. Ltd.

An AI-powered customer support ticket analytics system that allows users to query support ticket data using natural language and automatically detect anomalies.

The system combines an LLM, DuckDB, FastAPI, and Streamlit to provide a simple end-to-end AI application.

---

## 1. Project Overview

Customer support teams often have large numbers of support tickets containing information about priority, status, response time, resolution time, customer ratings, and assigned agents.

This project provides an AI-powered interface to analyze this data using natural-language questions.

### Example questions

- How many tickets are currently open?
- What is the average customer rating for Technical category tickets?
- Which agent resolved the most tickets?
- How many critical tickets are unresolved?
- Are there any anomalies in resolution times?

The system converts the user's natural-language question into a structured query intent using an LLM and then executes the corresponding operation against the ticket database.

---

# 2. Architecture

```text
                    ┌──────────────────────┐
                    │      Streamlit UI    │
                    │      Minimal UI      │
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI API     │
                    │                      │
                    │ /health              │
                    │ /query               │
                    │ /anomalies           │
                    └───────┬───────┬──────┘
                            │       │
                ┌───────────┘       └────────────┐
                ▼                                ▼
       ┌─────────────────┐              ┌─────────────────┐
       │      Ollama     │              │     DuckDB      │
       │    Llama 3.2    │              │ Ticket Database │
       │                 │              │                 │
       │ NL → Intent     │              │ SQL Analytics   │
       └─────────────────┘              └────────┬────────┘
                                                 │
                                                 ▼
                                      ┌────────────────────┐
                                      │ Anomaly Detection  │
                                      │                    │
                                      │ Aging Tickets      │
                                      │ Long Resolution    │
                                      └────────────────────┘

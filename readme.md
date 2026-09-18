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
```
# 3. Technology Stack
Component	Technology
Programming Language	Python
LLM	Llama 3.2
LLM Runtime	Ollama
API	FastAPI
Database / Analytics	DuckDB
Data Processing	Pandas
UI	Streamlit
Validation	Pydantic
Testing	Pytest
API Server	Uvicorn
# 4. Dataset

The system uses the provided:

data/support_tickets.csv

The dataset contains 500 customer support tickets.

Columns
Column	Description
ticket_id	Unique ticket identifier
created_at	Ticket creation timestamp
category	Ticket category
priority	Ticket priority
status	Ticket status
response_time_hrs	Response time in hours
resolution_time_hrs	Resolution time in hours
agent_id	Assigned support agent
customer_rating	Customer rating
issue_summary	Short description of the issue

For unresolved tickets, resolution_time_hrs and customer_rating can be null.

# 5. Project Structure
```
dotmappers-ai-assessment/
│
├── data/
│   └── support_tickets.csv
│
├── app/
│   ├── main.py
│   ├── data_loder.py
│   ├── query_engin.py
│   ├── llm.py
│   ├── anomoly.py
│   └── schemas.py
│
├── ui/
│   └── streamlit_app.py
│
├── test/
│   └── test_app.py
│
├── .env
├── .gitignore
├── requirements.txt
├── start.bat
└── README.md
```
# 6. How the System Works
### Step 1 — Load Dataset

The application loads the CSV dataset using Pandas.

The data is validated before being inserted into DuckDB.

Validation includes:

Required columns
Duplicate ticket IDs
Date conversion
Numeric field conversion
Missing categorical values
Negative numeric values
Customer rating range
### Step 2 — Store Data in DuckDB

DuckDB is used as the analytical database.

The CSV data is loaded into a DuckDB table:

support_tickets

This allows SQL-based analytical queries to be executed efficiently.

# 7. Natural Language Query Pipeline
```
The user enters a question such as:

How many tickets are currently open?

The question is sent to the local Llama 3.2 model through Ollama.

The LLM converts the question into a structured intent.

Example:

{
  "operation": "COUNT",
  "metric": null,
  "group_by": null,
  "filters": {
    "status": "Open"
  },
  "time_period": null
}

The query engine then converts this structured intent into a safe SQL query.

For example:

SELECT COUNT(*)
FROM support_tickets
WHERE status = 'Open';

The database result is returned through the FastAPI API.
```
# 8. Supported Query Operations

### The query engine supports the following operations:

```COUNT
AVERAGE
SUM
MIN
MAX
LIST
GROUP_BY
```
### Supported metrics include:

response_time_hrs
resolution_time_hrs
customer_rating

### Supported filters include:

category
priority
status
agent_id
9. Example Natural Language Query
Input
How many tickets are currently open?
LLM Intent
{
    "operation": "COUNT",
    "filters": {
        "status": "Open"
    }
}
Result
111
# 10. Another Example
Input
What is the average customer rating for Technical category tickets?

The LLM identifies:

Operation:
AVERAGE

Metric:
customer_rating

Filter:
category = Technical

The query engine executes the corresponding SQL query against DuckDB and returns the result.

# 11. Anomaly Detection

The system provides an anomaly detection endpoint.

Two types of anomalies are currently detected.

## 11.1 Unresolved High-Priority Tickets

The system checks for high-priority or critical tickets that remain unresolved for more than 24 hours.

The detection is based on:

priority
status
created_at

Example condition:

High/Critical priority
AND
Open/Unresolved
AND
older than 24 hours
## 11.2 Abnormally Long Resolution Times

The system uses the Interquartile Range (IQR) method to identify unusually long resolution times.

The upper threshold is calculated as:

Upper Bound = Q3 + 1.5 × IQR

Tickets above this threshold are flagged as anomalies.

This allows the system to identify unusually long resolution times without requiring manually defined thresholds.

# 12. REST API

The FastAPI backend exposes the required endpoints.

Health Check
GET /health

Example:

http://127.0.0.1:8000/health

Purpose:

Check whether the API is running.
Natural Language Query
POST /query

Example request:

{
  "question": "How many tickets are currently open?"
}

Example response:

{
  "question": "How many tickets are currently open?",
  "intent": {
    "operation": "COUNT",
    "metric": null,
    "group_by": null,
    "filters": {
      "status": "Open"
    },
    "time_period": null
  },
  "result": 111
}
Anomaly Detection
GET /anomalies

This endpoint returns detected anomalies including:

Unresolved high-priority tickets
Long resolution-time tickets
# 13. FastAPI Documentation

FastAPI automatically provides interactive API documentation.

After starting the API:

http://127.0.0.1:8000/docs

You can use Swagger UI to test the API endpoints.

# 14. Streamlit UI

The project includes a minimal Streamlit interface.

The UI provides:

Natural Language Query

Users can enter questions such as:

How many tickets are currently open?

and receive the result.

Anomaly Detection

Users can click the anomaly detection option to view detected abnormal tickets.

API Health

The UI checks whether the FastAPI backend is available.

# 15. LLM Integration

The project uses a local LLM through Ollama.

### Model:
```
Llama 3.2

The LLM is not directly responsible for executing database queries.

Instead, it performs natural-language understanding.

The pipeline is:

User Question
      ↓
Llama 3.2
      ↓
Structured Query Intent
      ↓
Query Engine
      ↓
DuckDB
      ↓
Result
```
This separates language understanding from database execution.

# 16. Why This Architecture?
LLM

Used for natural-language understanding.

This allows users to interact with the dataset without writing SQL.

DuckDB

Used for analytical SQL queries over the CSV dataset.

It is lightweight and well suited for local analytical workloads.

FastAPI

Provides a clean REST API layer and separates backend logic from the UI.

Streamlit

Provides a minimal user interface without requiring a separate frontend framework.

Pandas

Used for data loading, cleaning, type conversion, and anomaly calculations.

# 17. Installation
### Step 1 — Clone Repository
git clone https://github.com/naveenk-DS/dotmappers-ai-assessment.git
cd dotmappers-ai-assessment
### Step 2 — Create Virtual Environment

## Windows:
```
python -m venv .venv
```
## Activate:
```
.venv\Scripts\activate
Step 3 — Install Dependencies
pip install -r requirements.txt
```
# 18. Install and Run Ollama
```
Install Ollama and make sure it is running locally.

Pull the required model:

ollama pull llama3.2

Verify:

ollama list

The model should appear as:

llama3.2
19. Run the Application
Option 1 — Single Command

Windows:

start.bat

This starts:

FastAPI
Streamlit
Option 2 — Start API Manually
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
Start Streamlit

Open another terminal:

python -m streamlit run ui/streamlit_app.py
```
# 20. Running Tests

The project includes automated tests using Pytest.

Run:

pytest -q

Expected result:

4 passed

The tests cover:

Dataset loading
LLM intent understanding
Database query execution
Anomaly detection
# 21. Example Questions

The following natural-language questions can be used to test the system:

How many tickets are currently open?
What is the average customer rating for Technical category tickets?
How many critical tickets are unresolved?
Which agent resolved the most tickets?
Show me all Critical tickets not resolved within 12 hours.
Are there any anomalies in resolution times?
# 22. Error Handling

The application includes validation and error handling for:

Missing dataset
Invalid dataset columns
Invalid dates
Invalid numeric values
Duplicate ticket IDs
Invalid customer ratings
LLM failures
API failures
Database query failures

The system returns meaningful errors instead of silently producing incorrect results.

# 23. Limitations

The current implementation has some limitations.

Local LLM Dependency

The natural-language query functionality depends on Ollama and the local Llama 3.2 model.

Therefore, the evaluator needs Ollama and the model available when running the application locally.

Query Scope

The LLM currently supports a defined set of operations, metrics, filters, and grouping options.

Complex questions outside this supported intent schema may not be handled.

Dataset Size

The system was designed and tested against the provided 500-row dataset.

For significantly larger datasets, additional database optimization and deployment considerations would be required.

Time-Based Queries

Time-period interpretation is limited by the currently implemented intent schema.

# 24. Future Improvements

## Possible improvements include:

More advanced natural-language-to-SQL generation
Better query validation
Additional anomaly detection algorithms
Historical anomaly tracking
Dashboard visualizations
Authentication and authorization
Caching frequent queries
Structured logging
Monitoring and metrics
Docker-based deployment
Production database support
More comprehensive automated tests
Support for additional datasets
# 25. Security and Reliability Considerations

The LLM is used to generate a structured intent rather than directly executing arbitrary SQL.

This provides a controlled boundary between natural-language input and database execution.

The query engine only handles supported operations and fields.

Input validation is performed before processing the dataset.

# 26. Assessment Requirements Coverage
Requirement	Implementation
CSV ingestion	Pandas + DuckDB
Queryable data	DuckDB
Natural-language questions	Llama 3.2 + Ollama
LLM integration	app/llm.py
Query engine	app/query_engin.py
Anomaly detection	app/anomoly.py
REST API	FastAPI
Health endpoint	/health
NL query endpoint	/query
Anomaly endpoint	/anomalies
Minimal UI	Streamlit
Automated tests	Pytest
Documentation	README
Python implementation	Yes
Paid services	None
# 27. End-to-End Flow
                    User
                     │
                     ▼
             ┌───────────────┐
             │ Streamlit UI  │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │   FastAPI     │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │   Llama 3.2   │
             │    Ollama     │
             └───────┬───────┘
                     │
                     ▼
             Structured Intent
                     │
                     ▼
             ┌───────────────┐
             │ Query Engine  │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │    DuckDB     │
             └───────┬───────┘
                     │
                     ▼
                  Result
                     │
                     ▼
                 FastAPI
                     │
                     ▼
               Streamlit UI
# 28. Submission

GitHub Repository:

https://github.com/naveenk-DS/dotmappers-ai-assessment

The repository contains:

Source code
Dataset
REST API
Streamlit UI
Automated tests
Requirements
Documentation
# 29. Author

Naveen K

AI / GenAI Engineer

GitHub:

https://github.com/naveenk-DS


### One important thing before you submit

Your README currently uses the **actual filenames in your GitHub repository**:

- `data_loder.py`
- `query_engin.py`
- `anomoly.py`
- `test/test_app.py`

I kept those names in the README so it matches your current repository rather than silently changing them.

**However, before final submission, we should do one final GitHub + deployment check**, especially because your Re

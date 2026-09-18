from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.data_loder import load_database
from app.llm import understand_question
from app.query_engin import query_database
from app.anomoly import detect_anomalies


app = FastAPI(
    title="DOTMappers AI Support Ticket System",
    description="AI-powered customer support ticket analytics API",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "DOTMappers AI Assessment",
    }


@app.post("/query")
def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    connection = None

    try:
        connection = load_database()

        # Step 1: LLM understands the question
        intent = understand_question(request.question)

        # Step 2: DuckDB performs the actual calculation
        result = query_database(connection, intent)

        return {
            "question": request.question,
            "intent": intent,
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        if connection is not None:
            connection.close()


@app.get("/anomalies")
def anomalies():
    connection = None

    try:
        connection = load_database()

        results = detect_anomalies(connection)

        return results

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        if connection is not None:
            connection.close()
from app.data_loder import load_database
from app.llm import understand_question
from app.query_engin import query_database
from app.anomoly import detect_anomalies


def test_database_loads():
    connection = load_database()

    result = connection.execute(
        "SELECT COUNT(*) FROM support_tickets"
    ).fetchone()[0]

    assert result == 500

    connection.close()


def test_llm_understands_open_tickets():
    intent = understand_question(
        "How many tickets are currently open?"
    )

    assert intent["operation"] == "COUNT"
    assert intent["filters"]["status"].lower() == "open"


def test_query_engine():
    connection = load_database()

    intent = {
        "operation": "COUNT",
        "metric": None,
        "group_by": None,
        "filters": {"status": "Open"},
        "time_period": None,
    }

    result = query_database(connection, intent)

    assert result["result"] == 111

    connection.close()


def test_anomaly_detection():
    connection = load_database()

    results = detect_anomalies(connection)

    assert "unresolved_high_priority" in results
    assert "long_resolution_time" in results
    assert "anomalies" in results["long_resolution_time"]

    connection.close()
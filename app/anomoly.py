
import duckdb
import json

def detect_unresolved_old_tickets(
    connection: duckdb.DuckDBPyConnection,
    age_hours: float = 24,
) -> list[dict]:
    """
    Find high-priority unresolved tickets older than the given age.
    """

    query = """
        SELECT
            ticket_id,
            created_at,
            category,
            priority,
            status,
            response_time_hrs,
            resolution_time_hrs,
            agent_id,
            customer_rating,
            issue_summary,
            date_diff(
                'hour',
                created_at,
                CURRENT_TIMESTAMP
            ) AS age_hours
        FROM support_tickets
        WHERE LOWER(priority) IN ('high', 'critical')
          AND LOWER(status) IN ('open', 'unresolved')
          AND date_diff(
                'hour',
                created_at,
                CURRENT_TIMESTAMP
              ) > ?
        ORDER BY age_hours DESC
    """

    rows = connection.execute(query, [age_hours]).fetchdf()
    return json.loads(rows.to_json(orient="records", date_format="iso"))


def detect_long_resolution_times(
    connection: duckdb.DuckDBPyConnection,
) -> dict:
  
    stats_query = """
        SELECT
            quantile_cont(resolution_time_hrs, 0.25) AS q1,
            quantile_cont(resolution_time_hrs, 0.75) AS q3
        FROM support_tickets
        WHERE resolution_time_hrs IS NOT NULL
    """

    stats = connection.execute(stats_query).fetchone()

    if stats is None or stats[0] is None or stats[1] is None:
        return {
            "method": "IQR",
            "q1": None,
            "q3": None,
            "upper_bound": None,
            "anomalies": [],
        }

    q1 = float(stats[0])
    q3 = float(stats[1])

    iqr = q3 - q1
    upper_bound = q3 + (1.5 * iqr)

    anomaly_query = """
        SELECT
            ticket_id,
            created_at,
            category,
            priority,
            status,
            resolution_time_hrs,
            agent_id,
            issue_summary
        FROM support_tickets
        WHERE resolution_time_hrs IS NOT NULL
          AND resolution_time_hrs > ?
        ORDER BY resolution_time_hrs DESC
    """

    anomalies = connection.execute(anomaly_query, [upper_bound]).fetchdf()

    return {
        "method": "IQR",
        "q1": q1,
        "q3": q3,
        "upper_bound": upper_bound,
        "anomalies": anomalies,
    }


def detect_anomalies(
    connection: duckdb.DuckDBPyConnection,
) -> dict:
    """
    Run all anomaly detection checks.
    """

    unresolved_old = detect_unresolved_old_tickets(
        connection
    )

    long_resolution = detect_long_resolution_times(
        connection
    )

    return {
        "unresolved_high_priority": unresolved_old,
        "long_resolution_time": long_resolution,
    }


if __name__ == "__main__":
    from app.data_loder import load_database

    try:
        connection = load_database()

        results = detect_anomalies(connection)

        print("\n=== Unresolved High-Priority Tickets > 24 Hours ===")
        print(
            f"Found: {len(results['unresolved_high_priority'])}"
        )

        for ticket in results["unresolved_high_priority"][:10]:
            print(ticket)

        print("\n=== Long Resolution Time Anomalies ===")

        long_resolution = results["long_resolution_time"]

        print(f"Method: {long_resolution['method']}")
        print(f"Q1: {long_resolution['q1']}")
        print(f"Q3: {long_resolution['q3']}")
        print(
            f"Upper Bound: "
            f"{long_resolution['upper_bound']}"
        )
        print(
            f"Found: "
            f"{len(long_resolution['anomalies'])}"
        )

        for ticket in long_resolution["anomalies"][:10]:
            print(ticket)

        connection.close()

    except Exception as exc:
        print(f"\nError: {exc}")
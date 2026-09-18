import duckdb

ALLOWED_FILTERS = {
    "category",
    "priority",
    "status",
    "agent_id",
}

ALLOWED_METRICS = {
    "response_time_hrs",
    "resolution_time_hrs",
    "customer_rating",
}


def build_where_clause(filters: dict) -> tuple[str, list]:
    """Build a safe SQL WHERE clause from validated filters."""

    conditions = []
    parameters = []

    for field, value in filters.items():
        if field not in ALLOWED_FILTERS:
            raise ValueError(f"Unsupported filter: {field}")

        conditions.append(f'"{field}" = ?')
        parameters.append(value)

    if not conditions:
        return "", []

    return " WHERE " + " AND ".join(conditions), parameters


def execute_query(
    connection: duckdb.DuckDBPyConnection,
    intent: dict,
) -> dict:
    """Execute a structured LLM intent against DuckDB."""

    operation = intent["operation"]
    metric = intent.get("metric")
    group_by = intent.get("group_by")
    filters = intent.get("filters", {})

    where_clause, parameters = build_where_clause(filters)

    if metric is not None and metric not in ALLOWED_METRICS:
        raise ValueError(f"Unsupported metric: {metric}")

    if group_by is not None and group_by not in ALLOWED_FILTERS:
        raise ValueError(f"Unsupported group_by field: {group_by}")

    table = "support_tickets"

    # COUNT
    if operation == "COUNT":
        sql = f"""
            SELECT COUNT(*) AS count
            FROM {table}
            {where_clause}
        """

        result = connection.execute(sql, parameters).fetchone()[0]

        return {
            "operation": operation,
            "result": result,
        }

    # AVERAGE
    if operation == "AVERAGE":
        if not metric:
            raise ValueError("AVERAGE requires a metric.")

        sql = f"""
            SELECT AVG("{metric}") AS average
            FROM {table}
            {where_clause}
        """

        result = connection.execute(sql, parameters).fetchone()[0]

        return {
            "operation": operation,
            "metric": metric,
            "result": result,
        }

    # SUM
    if operation == "SUM":
        if not metric:
            raise ValueError("SUM requires a metric.")

        sql = f"""
            SELECT SUM("{metric}") AS total
            FROM {table}
            {where_clause}
        """

        result = connection.execute(sql, parameters).fetchone()[0]

        return {
            "operation": operation,
            "metric": metric,
            "result": result,
        }

    # MIN
    if operation == "MIN":
        if not metric:
            raise ValueError("MIN requires a metric.")

        sql = f"""
            SELECT MIN("{metric}") AS minimum
            FROM {table}
            {where_clause}
        """

        result = connection.execute(sql, parameters).fetchone()[0]

        return {
            "operation": operation,
            "metric": metric,
            "result": result,
        }

    # MAX
    if operation == "MAX":
        if not metric:
            raise ValueError("MAX requires a metric.")

        sql = f"""
            SELECT MAX("{metric}") AS maximum
            FROM {table}
            {where_clause}
        """

        result = connection.execute(sql, parameters).fetchone()[0]

        return {
            "operation": operation,
            "metric": metric,
            "result": result,
        }

    # GROUP BY
    if operation == "GROUP_BY":
        if not group_by:
            raise ValueError("GROUP_BY requires a group_by field.")

        sql = f"""
            SELECT
                "{group_by}" AS group_value,
                COUNT(*) AS count
            FROM {table}
            {where_clause}
            GROUP BY "{group_by}"
            ORDER BY count DESC
        """

        rows = connection.execute(sql, parameters).fetchall()

        return {
            "operation": operation,
            "group_by": group_by,
            "result": [
                {
                    "group_value": row[0],
                    "count": row[1],
                }
                for row in rows
            ],
        }

    # LIST
    if operation == "LIST":
        sql = f"""
            SELECT *
            FROM {table}
            {where_clause}
            LIMIT 100
        """

        rows = connection.execute(sql, parameters).fetchdf()

        return {
            "operation": operation,
            "result": rows.to_dict(orient="records"),
        }

    raise ValueError(f"Unsupported operation: {operation}")


def query_database(
    connection: duckdb.DuckDBPyConnection,
    intent: dict,
) -> dict:
    """
    Public function used by the rest of the application.
    """

    return execute_query(connection, intent)


if __name__ == "__main__":
    from app.data_loder import load_database
    from app.llm import understand_question

    question = input("Enter your question: ").strip()

    try:
        connection = load_database()

        intent = understand_question(question)

        print("\nLLM Intent:")
        print(intent)

        result = query_database(connection, intent)

        print("\nDatabase Result:")
        print(result)

        connection.close()

    except Exception as exc:
        print(f"\nError: {exc}")
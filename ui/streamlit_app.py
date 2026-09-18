import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Support Ticket AI",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Support Ticket AI Assistant")
st.caption("Ask questions about customer support tickets using natural language.")


# -----------------------------
# Health Check
# -----------------------------
try:
    health = requests.get(f"{API_URL}/health", timeout=5)

    if health.status_code == 200:
        st.success("API is connected")
    else:
        st.error("API is not healthy")

except requests.RequestException:
    st.error("Cannot connect to FastAPI. Start the API first.")


# -----------------------------
# Natural Language Query
# -----------------------------
st.header("Ask About Tickets")

question = st.text_input(
    "Enter your question",
    placeholder="How many tickets are currently open?",
)

if st.button("Ask AI"):

    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Understanding your question..."):

                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": question},
                    timeout=120,
                )

            if response.status_code == 200:

                data = response.json()

                st.subheader("Answer")

                result = data["result"]

                if isinstance(result, dict) and "result" in result:
                    st.metric("Result", result["result"])
                else:
                    st.write(result)

                with st.expander("LLM Intent"):
                    st.json(data["intent"])

            else:
                st.error(response.text)

        except requests.RequestException as exc:
            st.error(f"API error: {exc}")


# -----------------------------
# Anomaly Detection
# -----------------------------
st.header("Anomaly Detection")

if st.button("Detect Anomalies"):

    try:
        with st.spinner("Checking for anomalies..."):

            response = requests.get(
                f"{API_URL}/anomalies",
                timeout=30,
            )

        if response.status_code == 200:

            data = response.json()

            unresolved = data.get(
                "unresolved_high_priority",
                [],
            )

            long_resolution = data.get(
                "long_resolution_time",
                {},
            )

            st.subheader("High-Priority Unresolved Tickets")

            st.write(
                f"Found **{len(unresolved)}** tickets "
                "older than 24 hours."
            )

            if unresolved:
                st.dataframe(
                    unresolved,
                    use_container_width=True,
                )

            st.subheader("Long Resolution Time")

            st.write(
                f"Detection method: "
                f"**{long_resolution.get('method', 'N/A')}**"
            )

            st.write(
                f"Upper bound: "
                f"**{long_resolution.get('upper_bound', 'N/A')} hours**"
            )

            anomalies = long_resolution.get(
                "anomalies",
                [],
            )

            st.write(
                f"Found **{len(anomalies)}** anomalous tickets."
            )

            if anomalies:
                st.dataframe(
                    anomalies,
                    use_container_width=True,
                )

        else:
            st.error(response.text)

    except requests.RequestException as exc:
        st.error(f"API error: {exc}")
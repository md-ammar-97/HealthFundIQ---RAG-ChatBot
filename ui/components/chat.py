import streamlit as st
import requests
from ui.components.source_card import render_source_card

API_BASE = "http://localhost:8002"

EXAMPLE_CHIPS = [
    ("Expense ratio", "What is the expense ratio of HDFC Pharma and Healthcare Fund?"),
    ("Canada funds", "Which healthcare ETFs are available in Canada?"),
    ("XLV benchmark", "What benchmark does XLV track?"),
    ("Biotech focus", "Which funds in this corpus are biotech-focused?"),
    ("Country-wise", "Show healthcare funds available country-wise."),
    ("IBB holdings", "What are the top holdings of IBB?"),
    ("VHT objective", "What is the investment objective of VHT?"),
]


def render_welcome():
    st.markdown("""
    ### Ask. Compare. Verify.
    **Global healthcare funds — with facts, not financial advice.**

    Ask factual questions about healthcare, pharma, biotech, and med-tech funds
    across India, USA, Canada, China/HK, Japan, Singapore, and the UK.
    """)
    st.markdown("**Try one of these:**")
    cols = st.columns(4)
    for i, (label, query) in enumerate(EXAMPLE_CHIPS):
        if cols[i % 4].button(label, key=f"chip_{i}"):
            st.session_state["prefill_query"] = query
            st.rerun()


def _call_api(query: str, country: str | None, fund_id: str | None) -> dict | None:
    try:
        payload = {"query": query}
        if country:
            payload["country"] = country
        if fund_id:
            payload["fund_id"] = fund_id
        resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Backend unavailable. Start the FastAPI server first."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again."}
    except Exception as e:
        return {"error": str(e)}


def render_chat(country: str | None, fund_id: str | None):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        render_welcome()

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("source_url"):
                render_source_card(
                    source_url=msg["source_url"],
                    platform_url=msg.get("platform_url"),
                    last_updated=msg.get("last_updated"),
                    fetch_timestamp=msg.get("fetch_timestamp"),
                    source_type=msg.get("source_type", "official"),
                )

    # Pre-filled query from chip click
    prefill = st.session_state.pop("prefill_query", "")

    query = st.chat_input(
        "Ask about expense ratio, AUM, benchmark, holdings, risk rating, issuer...",
        key="chat_input",
    )
    query = query or prefill

    if query:
        # PII client-side check
        import re
        pii_patterns = [
            re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
            re.compile(r"\b[0-9]{12}\b"),
            re.compile(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+"),
        ]
        if any(p.search(query) for p in pii_patterns):
            st.warning(
                "Please do not share personal information (PAN, Aadhaar, email). "
                "HealthFundIQ only uses public fund sources."
            )
            return

        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Call API with loading state
        with st.chat_message("assistant"):
            with st.status("Processing...", expanded=False) as status:
                status.update(label="Classifying query...")
                data = _call_api(query, country, fund_id)
                status.update(label="Done", state="complete")

            if data is None or "error" in data:
                err_msg = data.get("error", "Unknown error") if data else "No response"
                st.error(f"Error: {err_msg}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {err_msg}"})
                return

            answer = data.get("answer", "No answer returned.")

            # Render answer
            if data.get("is_refusal"):
                st.warning(answer)
            elif data.get("missing_data"):
                st.info(answer)
            else:
                st.markdown(answer)

            # Source card
            if not data.get("is_refusal") and data.get("source_url"):
                render_source_card(
                    source_url=data.get("source_url"),
                    platform_url=data.get("platform_url"),
                    last_updated=data.get("last_updated"),
                    fetch_timestamp=data.get("fetch_timestamp"),
                )

        # Store in history
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "source_url": data.get("source_url"),
            "platform_url": data.get("platform_url"),
            "last_updated": data.get("last_updated"),
            "fetch_timestamp": data.get("fetch_timestamp"),
        })

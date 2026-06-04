import streamlit as st
import requests
import yaml

st.set_page_config(
    page_title="HealthFundIQ — Global Healthcare Funds Research",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components.sidebar import render_sidebar
from ui.components.chat import render_chat

# Apply custom CSS
with open("ui/assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Render sidebar and get filters
selected_country, selected_fund_id = render_sidebar()

# Top bar
st.markdown(
    "**HealthFundIQ** &nbsp;|&nbsp; Ask. Compare. Verify global healthcare funds — with facts, not financial advice.",
    unsafe_allow_html=True,
)
st.divider()

# Tabs
tab_ask, tab_explorer, tab_compare, tab_sources, tab_about = st.tabs([
    "💬 Ask AI", "🔍 Fund Explorer", "⚖️ Compare Funds", "📋 Sources", "ℹ️ About"
])

with tab_ask:
    render_chat(selected_country, selected_fund_id)

with tab_explorer:
    st.markdown("### Fund Explorer")
    try:
        params = {}
        if selected_country:
            params["country"] = selected_country
        resp = requests.get("http://localhost:8002/funds", params=params, timeout=5)
        funds = resp.json()
        if not funds:
            st.info("No funds found for the selected filter.")
        else:
            for fund in funds:
                if fund.get("is_backup"):
                    continue
                with st.expander(f"{fund['fund_name']} — {fund['country']}"):
                    col1, col2 = st.columns(2)
                    col1.markdown(f"**Type:** {fund['fund_type']}")
                    col1.markdown(f"**Subcategory:** {fund['domain_subcategory']}")
                    col1.markdown(f"**Currency:** {fund['currency']}")
                    col2.markdown(f"**Exchange:** {fund.get('exchange', 'N/A')}")
                    col2.markdown(f"**Ticker/ISIN:** {fund.get('ticker') or fund.get('isin') or 'N/A'}")
                    if fund.get("official_url"):
                        st.markdown(f"[Official Source]({fund['official_url']})")
                    st.markdown(f"[Platform Page]({fund['platform_url']})")
    except Exception as e:
        st.error(f"Could not load fund list: {e}")

with tab_compare:
    st.markdown("### Compare Funds")
    st.info(
        "Side-by-side factual comparison is coming in Phase 2. "
        "Use the **Ask AI** tab to compare specific funds by asking: "
        "'Compare the expense ratio of XLV and VHT' or 'Show Canada healthcare ETFs.'"
    )

with tab_sources:
    st.markdown("### Corpus Status")
    try:
        resp = requests.get("http://localhost:8002/health", timeout=5)
        h = resp.json()
        st.metric("Corpus Chunks", h.get("corpus_chunks", 0))
        st.caption(f"Last checked: {h.get('timestamp', 'N/A')}")
    except Exception:
        st.warning("Backend unavailable — cannot show corpus status.")

    st.markdown("---")
    st.markdown("View ingestion logs in `logs/ingestion.log` for per-fund status.")

with tab_about:
    st.markdown("""
    ### About HealthFundIQ

    **HealthFundIQ** is a facts-only RAG assistant for global healthcare, pharma, biotech,
    and med-tech funds. It retrieves factual information from public sources and answers
    questions with citations.

    **Markets covered:** India · USA · Canada · China/HK · Japan · Singapore · UK/Europe

    **What it can answer:** expense ratio, AUM, benchmark, NAV, top holdings, investment
    objective, risk rating, fund manager, fund house, and more.

    **What it cannot do:** investment advice, buy/sell recommendations, portfolio construction,
    return predictions, or personalized financial guidance.

    **Data freshness:** Corpus refreshes daily at 10:00 AM IST.

    ---
    **Disclaimer:** This assistant provides factual information from public sources only.
    Always verify details from official fund documents and consult a qualified financial
    adviser before making investment decisions.
    """)

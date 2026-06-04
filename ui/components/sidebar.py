import yaml
import streamlit as st


def _load_funds():
    with open("config/sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["funds"]


def render_sidebar() -> tuple[str | None, str | None]:
    """Returns (selected_country, selected_fund_id)."""
    with st.sidebar:
        st.markdown("## HealthFundIQ")
        st.caption("Ask. Compare. Verify.")
        st.divider()

        countries = [
            "All Countries", "India", "USA", "Canada",
            "China/HK", "Japan", "Singapore", "UK/Europe",
        ]
        country = st.selectbox("Country / Market", countries, key="country_filter")
        selected_country = None if country == "All Countries" else country

        # Dynamic fund list based on country
        all_funds = _load_funds()
        if selected_country:
            filtered = [f for f in all_funds if f["country"] == selected_country and not f.get("is_backup")]
        else:
            filtered = [f for f in all_funds if not f.get("is_backup")]

        fund_options = {"All Funds": None}
        for f in filtered:
            label = f["ticker"] + " — " + f["fund_name"] if f.get("ticker") else f["fund_name"]
            fund_options[label] = f["id"]

        selected_label = st.selectbox("Fund", list(fund_options.keys()), key="fund_filter")
        selected_fund_id = fund_options[selected_label]

        st.divider()

        from ui.components.disclaimer import render_disclaimer
        render_disclaimer()

    return selected_country, selected_fund_id

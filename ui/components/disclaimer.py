import streamlit as st


def render_disclaimer():
    st.info(
        "**Facts only. No investment advice.**\n\n"
        "This assistant provides factual information from public sources only. "
        "It does not provide investment advice, buy/sell recommendations, portfolio allocation, "
        "return predictions, or personalized financial guidance. "
        "Always verify details from official fund documents before making financial decisions."
    )

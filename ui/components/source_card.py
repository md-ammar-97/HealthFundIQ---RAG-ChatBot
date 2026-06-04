import streamlit as st


BADGE_HTML = {
    "official": '<span style="background:#DCFCE7;color:#15803D;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500;">Official</span>',
    "platform": '<span style="background:#F1F5F9;color:#475569;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500;">Platform</span>',
    "pdf":      '<span style="background:#FEF3C7;color:#B45309;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:500;">PDF</span>',
}


def render_source_card(
    source_url: str | None,
    platform_url: str | None,
    last_updated: str | None,
    fetch_timestamp: str | None,
    source_type: str = "official",
):
    if not source_url and not platform_url:
        return

    badge = BADGE_HTML.get(source_type, BADGE_HTML["platform"])

    with st.container():
        st.markdown("**Sources**")
        if source_url:
            st.markdown(
                f"{badge} [{source_url[:60]}...]({source_url})" if len(source_url) > 60
                else f"{badge} [{source_url}]({source_url})",
                unsafe_allow_html=True,
            )
        if platform_url and platform_url != source_url:
            st.markdown(f"Also see: [{platform_url[:50]}...]({platform_url})" if len(platform_url) > 50
                        else f"Also see: [{platform_url}]({platform_url})")
        if last_updated:
            st.caption(f"Last updated from sources: {last_updated}")
        if fetch_timestamp:
            st.caption(f"Fetched by HealthFundIQ: {fetch_timestamp[:19]} IST")

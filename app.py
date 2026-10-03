import streamlit as st

st.set_page_config(page_title="Analey", page_icon="favicon.svg", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

landing_page = st.Page("landing.py", title="Home", icon="🏠", url_path="", default=True)
auth_page = st.Page("auth.py", title="Sign in / Sign up", icon="🔐", url_path="auth")
dashboard_page = st.Page("dashboard.py", title="Dashboard", icon="📊 ", url_path="dashboard")

pages = [landing_page, auth_page, dashboard_page]   # always all three, unconditionally

nav = st.navigation(pages)
nav.run()
import streamlit as st

st.title('Analey')          # your app name
st.subheader('Your Business Data Analyst')       # tagline

st.write('Upload a CSV to get instant stats, charts, and AI-generated insights.')            # a sentence or two on what it does

if st.button("Get started →", type="primary"):
    st.switch_page("auth.py")
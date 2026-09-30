import streamlit as st

st.title("Sign in to Analey")

signin_tab, signup_tab = st.tabs(["Sign in", "Sign up"])

with signin_tab:
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([0.5, 1.5, 1])
    with col2:
        with st.form("signin_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type='password')

            btn1, btn2 = st.columns([0.35, 0.5])

            with btn2:
                submitted = st.form_submit_button("Sign in")
            

    if submitted:
        if not email or not password:
            st.error("Enter both email and password.")
        else:
            # TODO: real check goes here later
            st.session_state.user = {"email": email}
            st.switch_page('dashboard.py')



with signup_tab:

    col1, col2, col3 = st.columns([0.5, 1.5, 1])
    with col2:

        with st.form("signup_form"):
            first_name = st.text_input("Firstname")
            surname = st.text_input("Surname")
            email = st.text_input("Email")
            password = st.text_input("Password", type='password')
            confirm_password = st.text_input("Enter password again to confirm ", type='password')

            btn1, btn2 = st.columns([0.35, 0.5])

            with btn2:
                submitted_signup = st.form_submit_button("Create account")
            
            

    
    if submitted_signup:
        if not email or not password:
            st.error("Enter both email and password.")

        elif not first_name or not surname:
            st.error("Enter your First name or Surname.")

        elif password != confirm_password:
            st.error("Passwords do not match")
    
        else:
            try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                })
                st.session_state.user = {"email": email}
                st.switch_page("dashboard.py")
            except Exception as e:
                st.error(f"Sign up failed: {e}")


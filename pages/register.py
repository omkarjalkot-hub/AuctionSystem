import streamlit as st
import hashlib
from database.connection import get_connection


st.set_page_config(
    page_title="Register - SmartBid",
    page_icon="📝",
    layout="centered"
)


# ---------- Password Hashing ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- Page Header ----------

st.title("📝 Create Your SmartBid Account")
st.write("Join SmartBid and start participating in online auctions.")


# ---------- Registration Form ----------

with st.form("registration_form"):

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    submit = st.form_submit_button(
        "Create Account",
        use_container_width=True
    )


# ---------- Registration Logic ----------

if submit:

    if not first_name or not last_name or not email or not password:
        st.error("Please fill in all required fields.")

    elif password != confirm_password:
        st.error("Passwords do not match.")

    elif len(password) < 6:
        st.error("Password must contain at least 6 characters.")

    else:

        connection = get_connection()

        if connection:

            cursor = connection.cursor()

            # Check whether email already exists
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                st.error("An account with this email already exists.")

            else:

                password_hash = hash_password(password)

                cursor.execute(
                    """
                    INSERT INTO users
                    (first_name, last_name, email, password_hash)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        first_name,
                        last_name,
                        email,
                        password_hash
                    )
                )

                connection.commit()

                st.success(
                    "✅ Registration successful! "
                    "You can now log in to SmartBid."
                )

            cursor.close()
            connection.close()

        else:
            st.error(
                "Unable to connect to the SmartBid database."
            )


# ---------- Back to Login ----------

st.divider()

if st.button("🔐 Go to Login", use_container_width=True):
    st.switch_page("pages/Login.py")
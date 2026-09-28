import streamlit as st
import hashlib
from database.connection import get_connection


st.set_page_config(
    page_title="Login - SmartBid",
    page_icon="🔐",
    layout="centered"
)


# ---------- Password Hashing ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- Page Header ----------

st.title("🔐 Login to SmartBid")
st.write("Welcome back! Enter your account details to continue.")


# ---------- Login Form ----------

with st.form("login_form"):

    email = st.text_input("Email Address")

    password = st.text_input(
        "Password",
        type="password"
    )

    login_button = st.form_submit_button(
        "Login",
        use_container_width=True
    )


# ---------- Login Logic ----------

if login_button:

    if not email or not password:

        st.error("Please enter your email and password.")

    else:

        connection = get_connection()

        if connection:

            cursor = connection.cursor(dictionary=True)

            password_hash = hash_password(password)

            cursor.execute(
                """
                SELECT
                    user_id,
                    first_name,
                    last_name,
                    email,
                    role
                FROM users
                WHERE email = %s
                AND password_hash = %s
                """,
                (
                    email,
                    password_hash
                )
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()


            # ---------- Successful Login ----------

            if user:

                st.session_state.logged_in = True

                st.session_state.user_id = user["user_id"]

                st.session_state.first_name = user["first_name"]

                st.session_state.last_name = user["last_name"]

                st.session_state.email = user["email"]

                st.session_state.role = user["role"]


                st.success(
                    f"Welcome back, {user['first_name']}!"
                )


                # ---------- Redirect Based on Role ----------

                if user["role"] == "Admin":

                    st.switch_page("pages/admin.py")

                else:

                    st.switch_page("pages/Dashboard.py")


            else:

                st.error("Invalid email or password.")


        else:

            st.error(
                "Unable to connect to the SmartBid database."
            )


# ---------- Bottom Navigation ----------

st.divider()

st.write("Don't have a SmartBid account?")


if st.button(
    "📝 Create an Account",
    use_container_width=True
):

    st.switch_page("pages/Register.py")


if st.button(
    "🏠 Back to Home",
    use_container_width=True
):

    st.switch_page("app.py")
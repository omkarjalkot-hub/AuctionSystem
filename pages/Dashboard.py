import streamlit as st


# ---------- Page Configuration ----------

st.set_page_config(
    page_title="Dashboard - SmartBid",
    page_icon="🏠",
    layout="wide"
)


# ---------- Check Login ----------

if not st.session_state.get("logged_in", False):
    st.warning("Please login to access your dashboard.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/Login.py")

    st.stop()


# ---------- User Information ----------

first_name = st.session_state.get("first_name", "")
last_name = st.session_state.get("last_name", "")


# ---------- Header ----------

st.title("🏠 SmartBid Dashboard")

st.write(
    f"Welcome, **{first_name} {last_name}**! 👋"
)

st.divider()


# ---------- Navigation ----------

st.subheader("What would you like to do?")


col1, col2 = st.columns(2)


with col1:

    st.markdown("### 🔍 Browse Auctions")

    st.write(
        "Explore products currently available for bidding."
    )

    if st.button(
        "Browse Auctions",
        use_container_width=True
    ):
        st.switch_page("pages/Browse_Auction.py")


with col2:

    st.markdown("### ➕ Sell a Product")

    st.write(
        "Create your own auction and sell a product."
    )

    if st.button(
        "Sell Product",
        use_container_width=True
    ):
        st.switch_page("pages/Sell_Product.py")


# ---------- Account Sections ----------

st.divider()

st.subheader("Your Activity")


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown("### 🔨 My Bids")

    st.write(
        "View auctions where you have placed bids."
    )

    if st.button(
        "View My Bids",
        use_container_width=True
    ):
        st.switch_page("pages/My_Bids.py")


with col2:

    st.markdown("### 📦 My Auctions")

    st.write(
        "Manage the auctions you've created."
    )

    if st.button(
        "View My Auctions",
        use_container_width=True
    ):
        st.switch_page("pages/My_Auctions.py")


with col3:

    st.markdown("### 💳 Payments")

    st.write(
        "View your payment history."
    )

    if st.button(
        "View Payments",
        use_container_width=True
    ):
        st.switch_page("pages/Payment.py")


# ---------- Settings & Logout ----------

st.divider()


col1, col2 = st.columns(2)


with col1:

    if st.button(
        "⚙️ Settings",
        use_container_width=True
    ):
        st.switch_page("pages/Settings.py")


with col2:

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        # Clear login information
        for key in [
            "logged_in",
            "user_id",
            "first_name",
            "last_name",
            "email",
            "role"
        ]:
            st.session_state.pop(key, None)

        st.switch_page("app.py")
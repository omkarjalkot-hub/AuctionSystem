import streamlit as st
from database.connection import get_connection


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Admin Dashboard - SmartBid",
    page_icon="👑",
    layout="wide"
)


# ==========================================================
# ADMIN LOGIN CHECK
# ==========================================================

if not st.session_state.get("logged_in", False):

    st.warning("Please login first.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/Login.py")

    st.stop()


# ==========================================================
# ADMIN CHECK
# ==========================================================

user_role = st.session_state.get("role")

if user_role != "Admin":

    st.error(
        "🚫 Access Denied"
    )

    st.info(
        "Only administrators can access this page."
    )

    if st.button("🏠 Go to Dashboard"):
        st.switch_page("pages/Dashboard.py")

    st.stop()


# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("👑 Admin Dashboard")

st.write(
    "Welcome to the SmartBid administration panel."
)

st.divider()


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

connection = get_connection()

if not connection:

    st.error(
        "Unable to connect to the SmartBid database."
    )

    st.stop()


cursor = connection.cursor(dictionary=True)


# ==========================================================
# GET STATISTICS
# ==========================================================

# Total Users

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM users
    """
)

total_users = cursor.fetchone()["total"]


# Total Auctions

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM auction_items
    """
)

total_auctions = cursor.fetchone()["total"]


# Live Auctions

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM auction_items
    WHERE status = 'Live'
    """
)

live_auctions = cursor.fetchone()["total"]


# Scheduled Auctions

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM auction_items
    WHERE status = 'Scheduled'
    """
)

scheduled_auctions = cursor.fetchone()["total"]


# Ended Auctions

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM auction_items
    WHERE status = 'Ended'
    """
)

ended_auctions = cursor.fetchone()["total"]


# Sold Auctions

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM auction_items
    WHERE status = 'Sold'
    """
)

sold_auctions = cursor.fetchone()["total"]


# Total Bids

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM bids
    """
)

total_bids = cursor.fetchone()["total"]


# Total Winners

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM winners
    """
)

total_winners = cursor.fetchone()["total"]


# Total Payments

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM payments
    """
)

total_payments = cursor.fetchone()["total"]


# Paid Payments

cursor.execute(
    """
    SELECT COUNT(*) AS total
    FROM payments
    WHERE payment_status = 'Paid'
    """
)

paid_payments = cursor.fetchone()["total"]


# Total Revenue

cursor.execute(
    """
    SELECT COALESCE(SUM(amount), 0) AS total
    FROM payments
    WHERE payment_status = 'Paid'
    """
)

total_revenue = cursor.fetchone()["total"]


# ==========================================================
# CLOSE CONNECTION
# ==========================================================

cursor.close()
connection.close()


# ==========================================================
# USER STATISTICS
# ==========================================================

st.subheader("👥 User Statistics")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Total Users",
        total_users
    )

with col2:

    st.metric(
        "Total Bids",
        total_bids
    )


st.divider()


# ==========================================================
# AUCTION STATISTICS
# ==========================================================

st.subheader("🔨 Auction Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Total",
        total_auctions
    )

with col2:

    st.metric(
        "🟡 Scheduled",
        scheduled_auctions
    )

with col3:

    st.metric(
        "🟢 Live",
        live_auctions
    )

with col4:

    st.metric(
        "🔴 Ended",
        ended_auctions
    )

with col5:

    st.metric(
        "💵 Sold",
        sold_auctions
    )


st.divider()


# ==========================================================
# WINNER & PAYMENT STATISTICS
# ==========================================================

st.subheader("🏆 Winner & Payment Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Winners",
        total_winners
    )

with col2:

    st.metric(
        "Total Payments",
        total_payments
    )

with col3:

    st.metric(
        "Paid Payments",
        paid_payments
    )

with col4:

    st.metric(
        "Revenue",
        f"₹{float(total_revenue):,.2f}"
    )


st.divider()


# ==========================================================
# QUICK ACCESS
# ==========================================================

st.subheader("⚙️ Administration")

col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "👥 Manage Users",
        use_container_width=True
    ):

        st.session_state.admin_section = "users"

        st.rerun()


with col2:

    if st.button(
        "🔨 Manage Auctions",
        use_container_width=True
    ):

        st.session_state.admin_section = "auctions"

        st.rerun()


with col3:

    if st.button(
        "💳 View Payments",
        use_container_width=True
    ):

        st.session_state.admin_section = "payments"

        st.rerun()


# ==========================================================
# ADMIN USERS
# ==========================================================

if st.session_state.get("admin_section") == "users":

    st.divider()

    st.subheader("👥 All Users")

    connection = get_connection()

    if connection:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                user_id,
                first_name,
                last_name,
                email,
                role
            FROM users
            ORDER BY user_id DESC
            """
        )

        users = cursor.fetchall()

        cursor.close()
        connection.close()


        if users:

            st.dataframe(
                users,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No users found."
            )


# ==========================================================
# ADMIN AUCTIONS
# ==========================================================

if st.session_state.get("admin_section") == "auctions":

    st.divider()

    st.subheader("🔨 All Auctions")

    connection = get_connection()

    if connection:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                a.item_id,
                a.title,
                a.starting_price,
                a.start_time,
                a.end_time,
                a.status,
                CONCAT(
                    u.first_name,
                    ' ',
                    u.last_name
                ) AS seller
            FROM auction_items a

            LEFT JOIN users u
                ON a.seller_id = u.user_id

            ORDER BY a.item_id DESC
            """
        )

        auctions = cursor.fetchall()

        cursor.close()
        connection.close()


        if auctions:

            st.dataframe(
                auctions,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No auctions found."
            )


# ==========================================================
# ADMIN PAYMENTS
# ==========================================================

if st.session_state.get("admin_section") == "payments":

    st.divider()

    st.subheader("💳 Payment Records")

    connection = get_connection()

    if connection:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                p.payment_id,
                p.winner_id,
                p.amount,
                p.payment_method,
                p.payment_status,
                p.paid_at,
                w.item_id,
                w.user_id AS winner_user_id
            FROM payments p

            INNER JOIN winners w
                ON p.winner_id = w.winner_id

            ORDER BY p.payment_id DESC
            """
        )

        payments = cursor.fetchall()

        cursor.close()
        connection.close()


        if payments:

            st.dataframe(
                payments,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No payment records found."
            )


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()

if st.button(
    "🏠 Back to Dashboard",
    use_container_width=True
):

    st.switch_page(
        "pages/Dashboard.py"
    )
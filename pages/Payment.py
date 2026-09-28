import streamlit as st
from database.connection import get_connection


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Payment - SmartBid",
    page_icon="💳",
    layout="wide"
)


# ==========================================================
# LOGIN CHECK
# ==========================================================

if not st.session_state.get("logged_in", False):

    st.warning("Please login to make a payment.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/Login.py")

    st.stop()


# ==========================================================
# CURRENT USER
# ==========================================================

current_user_id = st.session_state.get("user_id")

if not current_user_id:

    st.error(
        "User information is missing. Please login again."
    )

    st.stop()


# ==========================================================
# SELECTED AUCTION
# ==========================================================

item_id = st.session_state.get("selected_item_id")

if not item_id:

    st.warning(
        "No auction selected for payment."
    )

    if st.button("🔨 Browse Auctions"):

        st.switch_page(
            "pages/Browse_Auction.py"
        )

    st.stop()


# ==========================================================
# GET WINNER
# ==========================================================

connection = get_connection()

if not connection:

    st.error(
        "Unable to connect to SmartBid database."
    )

    st.stop()


cursor = connection.cursor(
    dictionary=True
)


cursor.execute(
    """
    SELECT
        w.winner_id,
        w.item_id,
        w.user_id,
        w.winning_bid,
        w.won_at,
        a.title,
        a.seller_id
    FROM winners w

    INNER JOIN auction_items a
        ON w.item_id = a.item_id

    WHERE w.item_id = %s
    """,
    (item_id,)
)


winner = cursor.fetchone()


# ==========================================================
# WINNER NOT FOUND
# ==========================================================

if not winner:

    cursor.close()
    connection.close()

    st.error(
        "Winner information was not found."
    )

    if st.button("🔨 Back to Auction"):

        st.switch_page(
            "pages/Auction_Details.py"
        )

    st.stop()


# ==========================================================
# SECURITY CHECK
# ==========================================================

if winner["user_id"] != current_user_id:

    cursor.close()
    connection.close()

    st.error(
        "🚫 You are not the winner of this auction."
    )

    st.info(
        "Only the winning bidder can make the payment."
    )

    if st.button("🔨 Back to Auction"):

        st.switch_page(
            "pages/Auction_Details.py"
        )

    st.stop()


# ==========================================================
# CHECK EXISTING PAYMENT
# ==========================================================

cursor.execute(
    """
    SELECT
        payment_id,
        amount,
        payment_method,
        payment_status,
        paid_at
    FROM payments
    WHERE winner_id = %s
    """,
    (winner["winner_id"],)
)

existing_payment = cursor.fetchone()

cursor.close()
connection.close()


# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("💳 Auction Payment")

st.write(
    "Complete your payment for the auction you won."
)

st.divider()


# ==========================================================
# AUCTION INFORMATION
# ==========================================================

st.subheader("🏆 Winning Auction")

st.write(
    f"**Product:** {winner['title']}"
)

st.write(
    f"**Winning Bid:** "
    f"₹{winner['winning_bid']:,.2f}"
)

st.write(
    f"**Winner ID:** "
    f"{winner['winner_id']}"
)


# ==========================================================
# ALREADY PAID
# ==========================================================

if existing_payment:

    if existing_payment["payment_status"] == "Paid":

        st.success(
            "✅ Payment has already been completed!"
        )

        st.write(
            f"**Payment ID:** "
            f"{existing_payment['payment_id']}"
        )

        st.write(
            f"**Amount Paid:** "
            f"₹{existing_payment['amount']:,.2f}"
        )

        st.write(
            f"**Payment Method:** "
            f"{existing_payment['payment_method']}"
        )

        st.write(
            f"**Paid At:** "
            f"{existing_payment['paid_at']}"
        )

        st.divider()

        st.info(
            "Thank you for completing your payment."
        )


    else:

        st.warning(
            f"Previous payment status: "
            f"{existing_payment['payment_status']}"
        )


# ==========================================================
# PAYMENT FORM
# ==========================================================

if not existing_payment or existing_payment["payment_status"] != "Paid":

    st.subheader(
        "💰 Payment Details"
    )


    st.metric(
        "Amount to Pay",
        f"₹{winner['winning_bid']:,.2f}"
    )


    payment_method = st.selectbox(
        "Select Payment Method",
        [
            "UPI",
            "Card",
            "Net Banking"
        ]
    )


    st.divider()


    if st.button(
        "💳 Pay Now",
        use_container_width=True
    ):

        connection = get_connection()

        if not connection:

            st.error(
                "Unable to connect to database."
            )

            st.stop()


        cursor = connection.cursor()


        try:

            # ------------------------------------------------
            # Insert Payment
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO payments
                (
                    winner_id,
                    amount,
                    payment_method,
                    payment_status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    winner["winner_id"],
                    winner["winning_bid"],
                    payment_method,
                    "Paid"
                )
            )


            connection.commit()


            st.success(
                "🎉 Payment completed successfully!"
            )


            st.balloons()


            # ------------------------------------------------
            # Update Auction Status
            # ------------------------------------------------

            cursor.execute(
                """
                UPDATE auction_items
                SET status = 'Sold'
                WHERE item_id = %s
                """,
                (item_id,)
            )


            connection.commit()


            st.info(
                "🏷️ Auction has been marked as Sold."
            )


            st.write(
                f"**Payment Amount:** "
                f"₹{winner['winning_bid']:,.2f}"
            )

            st.write(
                f"**Payment Method:** "
                f"{payment_method}"
            )


            st.write(
                "Your payment has been recorded "
                "in the SmartBid database."
            )


        except Exception as error:

            connection.rollback()

            st.error(
                f"Payment failed: {error}"
            )


        finally:

            cursor.close()
            connection.close()


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()


col1, col2 = st.columns(2)


with col1:

    if st.button(
        "🔨 Back to Auction",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Auction_Details.py"
        )


with col2:

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )
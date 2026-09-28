import streamlit as st
from database.connection import get_connection
from datetime import datetime


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Auction Details - SmartBid",
    page_icon="🔨",
    layout="wide"
)


# ==========================================================
# LOGIN CHECK
# ==========================================================

if not st.session_state.get("logged_in", False):

    st.warning("Please login to access auction details.")

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

    st.warning("No auction selected.")

    if st.button("🔨 Go to Browse Auctions"):
        st.switch_page("pages/Browse_Auction.py")

    st.stop()


# ==========================================================
# GET AUCTION
# ==========================================================

connection = get_connection()

if not connection:

    st.error(
        "Unable to connect to the SmartBid database."
    )

    st.stop()


cursor = connection.cursor(dictionary=True)


query = """
SELECT
    a.item_id,
    a.seller_id,
    a.category_id,
    a.title,
    a.description,
    a.starting_price,
    a.bid_increment,
    a.start_time,
    a.end_time,
    a.image_path,
    a.status,

    c.category_name,

    CONCAT(
        u.first_name,
        ' ',
        u.last_name
    ) AS seller_name,

    COALESCE(
        (
            SELECT MAX(b.bid_amount)
            FROM bids b
            WHERE b.item_id = a.item_id
        ),
        a.starting_price
    ) AS current_bid

FROM auction_items a

LEFT JOIN categories c
    ON a.category_id = c.category_id

LEFT JOIN users u
    ON a.seller_id = u.user_id

WHERE a.item_id = %s
"""

cursor.execute(
    query,
    (item_id,)
)

auction = cursor.fetchone()

cursor.close()
connection.close()


# ==========================================================
# AUCTION NOT FOUND
# ==========================================================

if not auction:

    st.error("Auction not found.")

    if st.button("🔨 Back to Browse Auctions"):

        st.switch_page(
            "pages/Browse_Auctions.py"
        )

    st.stop()


# ==========================================================
# CURRENT TIME
# ==========================================================

now = datetime.now()

start_time = auction["start_time"]
end_time = auction["end_time"]


# ==========================================================
# DETERMINE CORRECT AUCTION STATUS
# ==========================================================

if now < start_time:

    correct_status = "Scheduled"

elif start_time <= now < end_time:

    correct_status = "Live"

else:

    correct_status = "Ended"


# ==========================================================
# UPDATE STATUS IN DATABASE
# ==========================================================

if auction["status"] != correct_status:

    connection = get_connection()

    if connection:

        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                UPDATE auction_items
                SET status = %s
                WHERE item_id = %s
                """,
                (
                    correct_status,
                    item_id
                )
            )

            connection.commit()

            auction["status"] = correct_status

        except Exception as error:

            connection.rollback()

            st.error(
                f"Unable to update auction status: {error}"
            )

        finally:

            cursor.close()
            connection.close()


# ==========================================================
# WINNER PROCESSING
# ==========================================================

existing_winner = None


if correct_status == "Ended":

    connection = get_connection()

    if connection:

        cursor = connection.cursor(
            dictionary=True
        )

        try:

            # ------------------------------------------------
            # Check if winner already exists
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    winner_id,
                    item_id,
                    user_id,
                    winning_bid,
                    won_at
                FROM winners
                WHERE item_id = %s
                """,
                (item_id,)
            )

            existing_winner = cursor.fetchone()


            # ------------------------------------------------
            # Create Winner
            # ------------------------------------------------

            if not existing_winner:

                cursor.execute(
                    """
                    SELECT
                        bidder_id,
                        bid_amount
                    FROM bids
                    WHERE item_id = %s
                    ORDER BY
                        bid_amount DESC,
                        bid_time ASC
                    LIMIT 1
                    """,
                    (item_id,)
                )

                highest_bid = cursor.fetchone()


                if highest_bid:

                    cursor.execute(
                        """
                        INSERT INTO winners
                        (
                            item_id,
                            user_id,
                            winning_bid
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            item_id,
                            highest_bid["bidder_id"],
                            highest_bid["bid_amount"]
                        )
                    )

                    connection.commit()


                    # Get newly created winner

                    cursor.execute(
                        """
                        SELECT
                            winner_id,
                            item_id,
                            user_id,
                            winning_bid,
                            won_at
                        FROM winners
                        WHERE item_id = %s
                        """,
                        (item_id,)
                    )

                    existing_winner = cursor.fetchone()


        except Exception as error:

            connection.rollback()

            st.error(
                f"Unable to determine winner: {error}"
            )


        finally:

            cursor.close()
            connection.close()


# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("🔨 Auction Details")

st.caption(
    f"Auction ID: {auction['item_id']}"
)

st.divider()


# ==========================================================
# PRODUCT LAYOUT
# ==========================================================

left_column, right_column = st.columns(
    [1, 1.3]
)


# ==========================================================
# PRODUCT IMAGE
# ==========================================================

with left_column:

    image_path = auction["image_path"]

    if image_path:

        try:

            st.image(
                image_path,
                use_container_width=True
            )

        except Exception:

            st.markdown(
                """
                <div style="
                    text-align:center;
                    font-size:120px;
                    padding:80px;
                ">
                    🔨
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            """
            <div style="
                text-align:center;
                font-size:120px;
                padding:80px;
            ">
                🔨
            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================================
# PRODUCT INFORMATION
# ==========================================================

with right_column:

    st.header(
        auction["title"]
    )


    # Category

    if auction["category_name"]:

        st.caption(
            f"📂 Category: "
            f"{auction['category_name']}"
        )


    # Description

    st.subheader(
        "📝 Description"
    )

    if auction["description"]:

        st.write(
            auction["description"]
        )

    else:

        st.write(
            "No description provided."
        )


    st.divider()


    # Seller

    if auction["seller_name"]:

        st.write(
            f"👤 **Seller:** "
            f"{auction['seller_name']}"
        )


    # Current bid

    st.metric(
        "Current Highest Bid",
        f"₹{auction['current_bid']:,.2f}"
    )


    st.write(
        f"💰 Starting Price: "
        f"₹{auction['starting_price']:,.2f}"
    )


    st.write(
        f"➕ Minimum Bid Increment: "
        f"₹{auction['bid_increment']:,.2f}"
    )


    # ======================================================
    # TIME
    # ======================================================

    st.write(
        f"🕐 **Starts:** "
        f"{start_time.strftime('%Y-%m-%d %I:%M %p')}"
    )


    st.write(
        f"⏰ **Ends:** "
        f"{end_time.strftime('%Y-%m-%d %I:%M %p')}"
    )


    # ======================================================
    # STATUS
    # ======================================================

    st.write(
        "**Auction Status:**"
    )


    if correct_status == "Scheduled":

        st.warning(
            "🟡 Auction is Scheduled"
        )


    elif correct_status == "Live":

        st.success(
            "🟢 Auction is Live"
        )


    elif correct_status == "Ended":

        st.error(
            "🔴 Auction Ended"
        )


# ==========================================================
# SCHEDULED AUCTION
# ==========================================================

if correct_status == "Scheduled":

    st.divider()

    st.info(
        "⏳ This auction has not started yet."
    )

    remaining = start_time - now

    total_seconds = int(
        remaining.total_seconds()
    )

    if total_seconds > 0:

        minutes = total_seconds // 60
        seconds = total_seconds % 60

        st.write(
            f"Starts in: **{minutes} minutes "
            f"{seconds} seconds**"
        )


# ==========================================================
# LIVE AUCTION
# ==========================================================

if correct_status == "Live":

    st.divider()

    st.subheader(
        "💰 Place Your Bid"
    )


    # ------------------------------------------------------
    # Seller cannot bid
    # ------------------------------------------------------

    if current_user_id == auction["seller_id"]:

        st.info(
            "🚫 You cannot bid on your own auction."
        )


    else:

        # --------------------------------------------------
        # Minimum bid
        # --------------------------------------------------

        minimum_bid = (
            float(auction["current_bid"])
            +
            float(auction["bid_increment"])
        )


        st.write(
            f"Minimum bid allowed: "
            f"**₹{minimum_bid:,.2f}**"
        )


        bid_amount = st.number_input(
            "Enter Your Bid",
            min_value=minimum_bid,
            value=minimum_bid,
            step=float(
                auction["bid_increment"]
            ),
            format="%.2f"
        )


        # --------------------------------------------------
        # Place Bid
        # --------------------------------------------------

        if st.button(
            "🔨 Place Bid",
            use_container_width=True
        ):

            if bid_amount < minimum_bid:

                st.error(
                    f"Your bid must be at least "
                    f"₹{minimum_bid:,.2f}"
                )

            else:

                connection = get_connection()

                if not connection:

                    st.error(
                        "Unable to connect to database."
                    )

                else:

                    cursor = None

                    try:

                        cursor = connection.cursor()


                        cursor.execute(
                            """
                            INSERT INTO bids
                            (
                                item_id,
                                bidder_id,
                                bid_amount
                            )
                            VALUES
                            (
                                %s,
                                %s,
                                %s
                            )
                            """,
                            (
                                item_id,
                                current_user_id,
                                bid_amount
                            )
                        )


                        connection.commit()


                        st.success(
                            "🎉 Your bid was placed successfully!"
                        )


                        st.rerun()


                    except Exception as error:

                        connection.rollback()

                        st.error(
                            f"Unable to place bid: {error}"
                        )


                    finally:

                        if cursor:

                            cursor.close()

                        connection.close()


# ==========================================================
# ENDED AUCTION
# ==========================================================

if correct_status == "Ended":

    st.divider()

    st.subheader(
        "🏆 Auction Result"
    )


    if existing_winner:

        winner_user_id = existing_winner[
            "user_id"
        ]

        winning_bid = existing_winner[
            "winning_bid"
        ]


        # --------------------------------------------------
        # Winner
        # --------------------------------------------------

        if current_user_id == winner_user_id:

            st.success(
                f"🎉 Congratulations! "
                f"You won this auction!"
            )

            st.markdown(
                f"### Winning Bid: "
                f"₹{winning_bid:,.2f}"
            )


            st.info(
                "💳 Payment will be available "
                "after we build the payment system."
            )


        # --------------------------------------------------
        # Other users
        # --------------------------------------------------

        else:

            st.info(
                "🏆 This auction has ended."
            )

            st.write(
                f"Winning Bid: "
                f"**₹{winning_bid:,.2f}**"
            )


    else:

        st.info(
            "No bids were placed on this auction."
        )


# ==========================================================
# NAVIGATION
# ==========================================================

st.divider()

col1, col2 = st.columns(2)


with col1:

    if st.button(
        "🔨 Back to Browse Auctions",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Browse_Auction.py"
        )


with col2:

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )
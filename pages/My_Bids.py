import streamlit as st
from database.connection import get_connection


# ---------- Page Configuration ----------

st.set_page_config(
    page_title="My Bids - SmartBid",
    page_icon="💰",
    layout="wide"
)


# ---------- Login Check ----------

if not st.session_state.get("logged_in", False):

    st.warning("Please login to view your bids.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/Login.py")

    st.stop()


# ---------- Current User ----------

user_id = st.session_state.get("user_id")

if not user_id:

    st.error("User information is missing.")
    st.stop()


# ---------- Page Header ----------

st.title("💰 My Bids")
st.write("Track the auctions where you have placed bids.")

st.divider()


# ---------- Database Connection ----------

connection = get_connection()

if not connection:

    st.error("Unable to connect to the SmartBid database.")
    st.stop()


cursor = connection.cursor(dictionary=True)


# ---------- Get User's Bids ----------

query = """
SELECT
    a.item_id,
    a.title,
    a.image_path,
    a.end_time,
    a.status,

    MAX(my_bids.bid_amount) AS my_bid,

    COALESCE(
        (
            SELECT MAX(all_bids.bid_amount)
            FROM bids all_bids
            WHERE all_bids.item_id = a.item_id
        ),
        a.starting_price
    ) AS current_highest_bid

FROM bids my_bids

JOIN auction_items a
    ON my_bids.item_id = a.item_id

WHERE my_bids.bidder_id = %s

GROUP BY
    a.item_id,
    a.title,
    a.image_path,
    a.end_time,
    a.status,
    a.starting_price

ORDER BY a.end_time ASC
"""


cursor.execute(
    query,
    (user_id,)
)

my_bids = cursor.fetchall()

cursor.close()
connection.close()


# ---------- No Bids ----------

if not my_bids:

    st.info(
        "You haven't placed any bids yet."
    )

    st.write(
        "Browse available auctions and place your first bid."
    )

    if st.button(
        "🔨 Browse Auctions",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Browse_Auction.py"
        )

    st.stop()


# ---------- Summary ----------

st.subheader(
    f"You have bid on {len(my_bids)} auction(s)"
)


# ---------- Display Bids ----------

for bid in my_bids:

    col1, col2, col3, col4 = st.columns(
        [1.5, 2, 2, 1]
    )


    # ---------- Image ----------

    with col1:

        image_path = bid["image_path"]

        if image_path:

            try:

                st.image(
                    image_path,
                    use_container_width=True
                )

            except:

                st.markdown(
                    "<div style='text-align:center;"
                    "font-size:60px;'>🔨</div>",
                    unsafe_allow_html=True
                )

        else:

            st.markdown(
                "<div style='text-align:center;"
                "font-size:60px;'>🔨</div>",
                unsafe_allow_html=True
            )


    # ---------- Auction Information ----------

    with col2:

        st.subheader(
            bid["title"]
        )

        st.write(
            f"⏰ Ends: {bid['end_time']}"
        )

        st.write(
            f"Status: {bid['status']}"
        )


    # ---------- Bid Information ----------

    with col3:

        st.write(
            "**My Latest Bid**"
        )

        st.markdown(
            f"### ₹{bid['my_bid']:,.2f}"
        )

        st.write(
            f"Current Highest Bid: "
            f"₹{bid['current_highest_bid']:,.2f}"
        )


        # Determine whether user is winning

        if (
            float(bid["my_bid"])
            >= float(bid["current_highest_bid"])
        ):

            st.success(
                "🟢 You are currently winning!"
            )

        else:

            st.error(
                "🔴 You have been outbid."
            )


    # ---------- View Auction ----------

    with col4:

        st.write("")

        if st.button(
            "View Auction",
            key=f"my_bid_{bid['item_id']}",
            use_container_width=True
        ):

            st.session_state.selected_item_id = (
                bid["item_id"]
            )

            st.switch_page(
                "pages/Auction_Details.py"
            )


    st.divider()


# ---------- Navigation ----------

col1, col2 = st.columns(2)


with col1:

    if st.button(
        "🔨 Browse Auctions",
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
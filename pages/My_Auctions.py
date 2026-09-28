import streamlit as st
from database.connection import get_connection


# ---------- Page Configuration ----------

st.set_page_config(
    page_title="My Auctions - SmartBid",
    page_icon="📦",
    layout="wide"
)


# ---------- Login Check ----------

if not st.session_state.get("logged_in", False):

    st.warning("Please login to view your auctions.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/Login.py")

    st.stop()


# ---------- Current User ----------

user_id = st.session_state.get("user_id")

if not user_id:

    st.error("User information is missing.")
    st.stop()


# ---------- Page Header ----------

st.title("📦 My Auctions")
st.write("Manage and monitor the auctions you have created.")

st.divider()


# ---------- Database Connection ----------

connection = get_connection()

if not connection:

    st.error("Unable to connect to the SmartBid database.")
    st.stop()


cursor = connection.cursor(dictionary=True)


# ---------- Get Seller's Auctions ----------

query = """
SELECT
    a.item_id,
    a.title,
    a.description,
    a.starting_price,
    a.bid_increment,
    a.start_time,
    a.end_time,
    a.image_path,
    a.status,
    c.category_name,

    COALESCE(
        (
            SELECT MAX(b.bid_amount)
            FROM bids b
            WHERE b.item_id = a.item_id
        ),
        a.starting_price
    ) AS current_highest_bid,

    (
        SELECT COUNT(*)
        FROM bids b2
        WHERE b2.item_id = a.item_id
    ) AS total_bids

FROM auction_items a

LEFT JOIN categories c
    ON a.category_id = c.category_id

WHERE a.seller_id = %s

ORDER BY a.end_time ASC
"""


cursor.execute(
    query,
    (user_id,)
)

my_auctions = cursor.fetchall()

cursor.close()
connection.close()


# ---------- No Auctions ----------

if not my_auctions:

    st.info(
        "You haven't created any auctions yet."
    )

    if st.button(
        "➕ Create Your First Auction",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Sell_Product.py"
        )

    st.stop()


# ---------- Summary ----------

st.subheader(
    f"You have created {len(my_auctions)} auction(s)"
)


# ---------- Display Auctions ----------

for auction in my_auctions:

    col1, col2, col3, col4 = st.columns(
        [1.3, 2, 2, 1]
    )


    # ---------- Image ----------

    with col1:

        image_path = auction["image_path"]

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
            auction["title"]
        )

        if auction["category_name"]:

            st.caption(
                f"📂 {auction['category_name']}"
            )

        st.write(
            f"🕐 Starts: {auction['start_time']}"
        )

        st.write(
            f"⏰ Ends: {auction['end_time']}"
        )

        st.write(
            f"Status: {auction['status']}"
        )


    # ---------- Bid Information ----------

    with col3:

        st.write(
            "**Current Highest Bid**"
        )

        st.markdown(
            f"### ₹{auction['current_highest_bid']:,.2f}"
        )

        st.write(
            f"Starting Price: "
            f"₹{auction['starting_price']:,.2f}"
        )

        st.write(
            f"Total Bids: "
            f"{auction['total_bids']}"
        )


    # ---------- View Auction ----------

    with col4:

        st.write("")

        if st.button(
            "View Auction",
            key=f"my_auction_{auction['item_id']}",
            use_container_width=True
        ):

            st.session_state.selected_item_id = (
                auction["item_id"]
            )

            st.switch_page(
                "pages/Auction_Details.py"
            )


    st.divider()


# ---------- Navigation ----------

col1, col2 = st.columns(2)


with col1:

    if st.button(
        "🛍️ Create New Auction",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Sell_Product.py"
        )


with col2:

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )
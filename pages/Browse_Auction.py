import streamlit as st
from database.connection import get_connection


# ---------- Page Configuration ----------

st.set_page_config(
    page_title="Browse Auctions - SmartBid",
    page_icon="🔨",
    layout="wide"
)


# ---------- Check Login ----------

if not st.session_state.get("logged_in", False):

    st.warning("Please login to access auctions.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/Login.py")

    st.stop()


# ---------- Page Header ----------

st.title("🔨 Browse Auctions")
st.write("Explore products and find your next great deal.")

st.divider()


# ---------- Get Auctions ----------

connection = get_connection()

if not connection:
    st.error("Unable to connect to the SmartBid database.")
    st.stop()


cursor = connection.cursor(dictionary=True)

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
    COALESCE(MAX(b.bid_amount), a.starting_price) AS current_bid

FROM auction_items a

LEFT JOIN categories c
    ON a.category_id = c.category_id

LEFT JOIN bids b
    ON a.item_id = b.item_id

GROUP BY
    a.item_id,
    a.title,
    a.description,
    a.starting_price,
    a.bid_increment,
    a.start_time,
    a.end_time,
    a.image_path,
    a.status,
    c.category_name

ORDER BY a.end_time ASC
"""

cursor.execute(query)

auctions = cursor.fetchall()

cursor.close()
connection.close()


# ---------- Display Auctions ----------

if not auctions:

    st.info(
        "There are currently no auctions available."
    )

    st.write(
        "Create an auction from the Sell Product section "
        "to see it here."
    )

else:

    st.subheader(
        f"Available Auctions ({len(auctions)})"
    )

    # Display 3 auction cards per row

    for i in range(0, len(auctions), 3):

        columns = st.columns(3)

        for j, column in enumerate(columns):

            if i + j >= len(auctions):
                break

            auction = auctions[i + j]

            with column:

                # ---------- Image ----------

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
                            "font-size:70px;'>🔨</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        "<div style='text-align:center;"
                        "font-size:70px;'>🔨</div>",
                        unsafe_allow_html=True
                    )


                # ---------- Product Information ----------

                st.subheader(auction["title"])

                if auction["category_name"]:
                    st.caption(
                        f"📂 {auction['category_name']}"
                    )

                description = auction["description"]

                if description:

                    if len(description) > 100:
                        description = description[:100] + "..."

                    st.write(description)


                # ---------- Current Bid ----------

                st.markdown(
                    f"### Current Bid: ₹"
                    f"{auction['current_bid']:,.2f}"
                )

                st.write(
                    f"Minimum Bid Increment: "
                    f"₹{auction['bid_increment']:,.2f}"
                )


                # ---------- Auction Time ----------

                st.write(
                    f"🕐 Starts: "
                    f"{auction['start_time']}"
                )

                st.write(
                    f"⏰ Ends: "
                    f"{auction['end_time']}"
                )


                # ---------- View Auction ----------

                if st.button(
                    "View Auction",
                    key=f"view_{auction['item_id']}",
                    use_container_width=True
                ):

                    st.session_state.selected_item_id = (
                        auction["item_id"]
                    )

                    st.switch_page(
                        "pages/Auction_Details.py"
                    )


# ---------- Back to Dashboard ----------

st.divider()

if st.button(
    "🏠 Back to Dashboard",
    use_container_width=True
):
    st.switch_page("pages/Dashboard.py")
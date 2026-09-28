import streamlit as st
from database.connection import get_connection
from datetime import datetime, timedelta
import os


# ---------- Page Configuration ----------

st.set_page_config(
    page_title="Sell Product - SmartBid",
    page_icon="🛍️",
    layout="wide"
)


# ---------- Login Check ----------

if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")

    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")

    st.stop()


# ---------- Get Logged-in User ----------

user_id = st.session_state.get("user_id")

if not user_id:
    st.error("User information is missing. Please login again.")
    st.stop()


# ---------- Page Header ----------

st.title("🛍️ Sell Your Product")
st.write("Create an auction and let buyers compete for your product.")

st.divider()


# ---------- Load Categories ----------

connection = get_connection()

if not connection:
    st.error("Unable to connect to the SmartBid database.")
    st.stop()

cursor = connection.cursor(dictionary=True)

cursor.execute("""
    SELECT category_id, category_name
    FROM categories
    ORDER BY category_name
""")

categories = cursor.fetchall()

cursor.close()
connection.close()


if not categories:
    st.error("No categories are available.")
    st.stop()


# ---------- Category Dictionary ----------

category_options = {
    category["category_name"]: category["category_id"]
    for category in categories
}


# ---------- Product Form ----------

st.subheader("📦 Product Information")

with st.form("sell_product_form"):

    title = st.text_input(
        "Product Title",
        placeholder="Example: iPhone 15 Pro"
    )

    description = st.text_area(
        "Product Description",
        placeholder="Describe the condition, features and other important details..."
    )

    category_name = st.selectbox(
        "Category",
        list(category_options.keys())
    )

    col1, col2 = st.columns(2)

    with col1:

        starting_price = st.number_input(
            "Starting Price (₹)",
            min_value=1.0,
            value=1000.0,
            step=100.0
        )

    with col2:

        bid_increment = st.number_input(
            "Minimum Bid Increment (₹)",
            min_value=1.0,
            value=100.0,
            step=50.0
        )


    st.subheader("⏰ Auction Timing")

    col3, col4 = st.columns(2)

    default_start = datetime.now() + timedelta(minutes=5)
    default_end = default_start + timedelta(days=1)

    with col3:

        start_date = st.date_input(
            "Start Date",
            value=default_start.date()
        )

        start_time = st.time_input(
            "Start Time",
            value=default_start.time().replace(second=0, microsecond=0)
        )

    with col4:

        end_date = st.date_input(
            "End Date",
            value=default_end.date()
        )

        end_time = st.time_input(
            "End Time",
            value=default_end.time().replace(second=0, microsecond=0)
        )


    st.subheader("📷 Product Image")

    uploaded_image = st.file_uploader(
        "Upload one product image",
        type=["jpg", "jpeg", "png", "webp"]
    )


    st.divider()

    create_auction = st.form_submit_button(
        "🔨 Create Auction",
        use_container_width=True
    )


# ---------- Create Auction ----------

if create_auction:

    # Basic validation

    if not title.strip():

        st.error("Please enter a product title.")
        st.stop()


    if not description.strip():

        st.error("Please enter a product description.")
        st.stop()


    if starting_price <= 0:

        st.error("Starting price must be greater than ₹0.")
        st.stop()


    if bid_increment <= 0:

        st.error("Bid increment must be greater than ₹0.")
        st.stop()


    # Combine date and time

    auction_start = datetime.combine(
        start_date,
        start_time
    )

    auction_end = datetime.combine(
        end_date,
        end_time
    )


    # Check timing

    if auction_end <= auction_start:

        st.error(
            "End date and time must be after the start date and time."
        )
        st.stop()


    # Save image

    image_path = None

    if uploaded_image:

        image_folder = os.path.join(
            "assets",
            "images"
        )

        os.makedirs(
            image_folder,
            exist_ok=True
        )

        file_extension = os.path.splitext(
            uploaded_image.name
        )[1].lower()

        file_name = (
            f"auction_{user_id}_"
            f"{int(datetime.now().timestamp())}"
            f"{file_extension}"
        )

        full_image_path = os.path.join(
            image_folder,
            file_name
        )

        with open(full_image_path, "wb") as file:

            file.write(
                uploaded_image.getbuffer()
            )

        image_path = full_image_path


    # ---------- Insert into Database ----------

    connection = get_connection()

    if not connection:

        st.error(
            "Unable to connect to the SmartBid database."
        )
        st.stop()


    cursor = connection.cursor()


    query = """
        INSERT INTO auction_items
        (
            seller_id,
            category_id,
            title,
            description,
            starting_price,
            bid_increment,
            start_time,
            end_time,
            image_path
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """


    values = (
        user_id,
        category_options[category_name],
        title.strip(),
        description.strip(),
        starting_price,
        bid_increment,
        auction_start,
        auction_end,
        image_path
    )


    try:

        cursor.execute(
            query,
            values
        )

        connection.commit()

        st.success(
            "🎉 Auction created successfully!"
        )

        st.balloons()

        st.write(
            f"**Product:** {title}"
        )

        st.write(
            f"**Category:** {category_name}"
        )

        st.write(
            f"**Starting Price:** ₹{starting_price:,.2f}"
        )

        st.write(
            f"**Bid Increment:** ₹{bid_increment:,.2f}"
        )

        st.write(
            f"**Starts:** {auction_start}"
        )

        st.write(
            f"**Ends:** {auction_end}"
        )


    except Exception as error:

        connection.rollback()

        st.error(
            f"Could not create auction: {error}"
        )


    finally:

        cursor.close()
        connection.close()


# ---------- Navigation ----------

st.divider()

col5, col6 = st.columns(2)

with col5:

    if st.button(
        "🔨 Browse Auctions",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Browse_Auction.py"
        )


with col6:

    if st.button(
        "🏠 Dashboard",
        use_container_width=True
    ):

        st.switch_page(
            "pages/Dashboard.py"
        )
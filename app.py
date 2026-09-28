import streamlit as st


# Page configuration
st.set_page_config(
    page_title="SmartBid",
    page_icon="🔨",
    layout="centered"
)


# ---------- Custom CSS ----------

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #f8fafc;
    }

    /* SmartBid title */
    .smartbid-title {
        text-align: center;
        font-size: 52px;
        font-weight: 800;
        color: #2563EB;
        margin-top: 60px;
        margin-bottom: 5px;
    }

    /* Tagline */
    .smartbid-tagline {
        text-align: center;
        font-size: 20px;
        color: #475569;
        margin-bottom: 35px;
    }

    /* Trust text */
    .trust-text {
        text-align: center;
        color: #64748b;
        font-size: 15px;
        margin-top: 25px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
    }

</style>
""", unsafe_allow_html=True)


# ---------- Homepage ----------

st.markdown(
    '<div class="smartbid-title">SMARTBID</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="smartbid-tagline">Bid Smart. Win Smarter.</div>',
    unsafe_allow_html=True
)


# ---------- Main Buttons ----------

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "🔐 Login",
        use_container_width=True
    ):
        st.switch_page("pages/Login.py")


with col2:

    if st.button(
        "📝 Register",
        use_container_width=True
    ):
        st.switch_page("pages/Register.py")


# ---------- Auction Image ----------

st.markdown(
    """
    <div style="
        text-align:center;
        font-size:80px;
        margin-top:45px;
        margin-bottom:20px;
    ">
        🔨
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="trust-text">Secure • Simple • Trusted Auctions</div>',
    unsafe_allow_html=True
)


# ---------- Footer ----------

st.markdown(
    """
    <div class="footer">
        © 2026 SmartBid
    </div>
    """,
    unsafe_allow_html=True
)


# ---------- Admin Login ----------

st.markdown(
    "<div style='text-align:center; margin-top:15px;'>",
    unsafe_allow_html=True
)

if st.button(
    "🔑 Admin Login",
    use_container_width=True
):
    st.switch_page("pages/Login.py")

st.markdown(
    "</div>",
    unsafe_allow_html=True
)
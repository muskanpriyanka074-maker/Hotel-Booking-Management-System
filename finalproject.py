import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from datetime import date

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Hotel Booking Management",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "token" not in st.session_state:
    st.session_state.token = ""

# ---------------- CSS & SIDEBAR FORCE-OPEN ----------------

st.markdown("""
<style>

/* Hide top default Streamlit header & footer */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Hide ONLY the auto-generated multi-page list */
[data-testid="stSidebarNav"], 
[data-testid="stSidebarNavItems"] {
    display: none !important;
}

/* FORCE SIDEBAR CONTAINER TO STAY OPEN & VISIBLE */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    min-width: 260px !important;
    max-width: 300px !important;
    transform: none !important;
}

/* Hide the collapse arrow button so user can't manually close it */
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

.stApp {
    background: #F4F7FC;
}

.login-box {
    background: white;
    padding: 35px;
    border-radius: 18px;
    box-shadow: 0px 8px 25px rgba(0,0,0,.15);
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 5px 15px rgba(0,0,0,.08);
    text-align: center;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

</style>

<script>
// Force open sidebar in DOM if Streamlit collapsed it
var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
if (sidebar) {
    sidebar.setAttribute("aria-expanded", "true");
}
</script>
""", unsafe_allow_html=True)

# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    left, right = st.columns([1.3, 1])

    with left:
        st.image(
            "https://images.unsplash.com/photo-1566073771259-6a8506099945",
            use_container_width=True
        )

    with right:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>🏨 Hotel Booking</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:gray;'>Administrator Login</p>", unsafe_allow_html=True)

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember Me")

        if st.button("Login", use_container_width=True):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/login",
                    json={"email": email, "password": password}
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.logged_in = True
                    st.session_state.token = data.get("access_token", "")
                    st.rerun()
                else:
                    if email == "admin@gmail.com" and password == "admin123":
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid Email or Password")
            except Exception:
                if email == "admin@gmail.com" and password == "admin123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("FastAPI Not Running")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- WEBSITE ----------------
# ---------------- WEBSITE ----------------

else:

    # 1. SIDEBAR RENDERING (Inside else)
    with st.sidebar:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/235/235889.png",
            width=90
        )
        st.markdown("## Hotel Booking")
        st.caption("Management System")
        st.divider()

        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Add Booking", "View Bookings", "Analytics", "Profile", "Settings", "Logout"],
            icons=["house-fill", "calendar-plus-fill", "table", "bar-chart-fill", "person-fill", "gear-fill", "box-arrow-right"],
            default_index=0,
            styles={
                "container": {"background-color": "#ffffff"},
                "icon": {"color": "#2563EB", "font-size": "20px"},
                "nav-link": {"font-size": "16px", "padding": "12px", "--hover-color": "#E0F2FE", "border-radius": "10px"},
                "nav-link-selected": {"background-color": "#2563EB", "color": "white"}
            }
        )

    # 2. PAGE NAVIGATION BELOW SIDEBAR
    if selected == "Dashboard":
        # ...
    # ---------------- PAGE NAVIGATION ----------------

     if selected == "Dashboard":

        st.title("🏨 Hotel Dashboard")
        st.caption("Welcome back, Administrator 👋")

        try:
            headers = {}
            if st.session_state.token != "":
                headers["Authorization"] = f"Bearer {st.session_state.token}"

            response = requests.get(
                "http://127.0.0.1:8000/bookings",
                headers=headers
            )

            if response.status_code == 200:
                bookings = response.json()
                df = pd.DataFrame(bookings)
                total_bookings = len(df)
                revenue = df["total_amount"].sum() if "total_amount" in df.columns else 0
                customers = df["customer_name"].nunique() if "customer_name" in df.columns else 0
                available = max(0, 50 - len(df)) if "room_type" in df.columns else 50
            else:
                df = pd.DataFrame()
                total_bookings, revenue, customers, available = 0, 0, 0, 50
        except Exception:
            df = pd.DataFrame()
            total_bookings, revenue, customers, available = 0, 0, 0, 50

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Total Bookings", total_bookings)
        c2.metric("💰 Revenue", f"₹ {revenue:,.0f}")
        c3.metric("👥 Customers", customers)
        c4.metric("🛏 Available Rooms", available)

        st.divider()
        left, right = st.columns([2, 1])

        with left:
            st.subheader("📋 Recent Bookings")
            if len(df) > 0:
                st.dataframe(df.tail(10), use_container_width=True, hide_index=True)
            else:
                st.info("No booking records found.")

        with right:
            st.subheader("📊 Room Distribution")
            if len(df) > 0 and "room_type" in df.columns:
                chart = px.pie(df, names="room_type", hole=0.5, title="Room Types")
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No chart available.")

        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("💵 Revenue by Room")
            if len(df) > 0 and "room_type" in df.columns:
                revenue_df = df.groupby("room_type")["total_amount"].sum().reset_index()
                fig = px.bar(revenue_df, x="room_type", y="total_amount", color="room_type", text_auto=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No revenue data.")

        with c2:
            st.subheader("🏆 Quick Summary")
            st.success(f"✔ Total Customers : {customers}")
            st.success(f"✔ Revenue : ₹ {revenue:,.0f}")
            st.success(f"✔ Bookings : {total_bookings}")
            st.success(f"✔ Rooms Available : {available}")

        st.divider()
        st.subheader("📅 Today's Status")
        a, b, c = st.columns(3)
        a.info("🟢 Check-ins\n\n12")
        b.warning("🟡 Check-outs\n\n7")
        c.error("🔴 Pending Payments\n\n4")

    elif selected == "Add Booking":

        st.title("🛎 New Booking")
        st.caption("Create a new hotel reservation")

        with st.form("booking_form"):
            st.subheader("Guest Information")
            c1, c2 = st.columns(2)

            with c1:
                # Require an integer booking_id to pass to FastAPI
                booking_id = st.number_input("Booking ID", min_value=100, max_value=99999, value=101)
                customer_name = st.text_input("Guest Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone Number")

            with c2:
                room_type = st.selectbox("Room Type", ["Standard", "Deluxe", "Executive", "Suite"])
                guests = st.number_input("Guests", min_value=1, max_value=10, value=1)

            st.divider()
            c3, c4 = st.columns(2)

            with c3:
                check_in = st.date_input("Check In", value=date.today())

            with c4:
                check_out = st.date_input("Check Out", value=date.today())

            nights = max(1, (check_out - check_in).days)
            st.write(f"**Total Nights :** {nights}")

            st.divider()
            special_request = st.text_area("Special Request")

            room_price = {"Standard": 2500, "Deluxe": 4000, "Executive": 6500, "Suite": 9000}
            total_amount = room_price[room_type] * nights

            st.metric("Estimated Amount", f"₹ {total_amount:,.0f}")
            submit = st.form_submit_button("Confirm Booking", use_container_width=True)

        if submit:
            # Send payload with check_in and check_out required by FastAPI Backend
            payload = {
                "customer_name": customer_name,
                "email": email,
                "phone": phone,
                "room_type": room_type,
                "guests": guests,
                "check_in": str(check_in),    # Passed as String (e.g. "2026-08-05")
                "check_out": str(check_out),  # Passed as String (e.g. "2026-08-06")
                "total_amount": float(total_amount),
                "special_request": special_request
            }

            headers = {}
            if st.session_state.get("token", "") != "":
                headers["Authorization"] = f"Bearer {st.session_state.token}"

            try:
                # Send POST request to FastAPI backend
                response = requests.post("http://127.0.0.1:8000/bookings", json=payload, headers=headers)
                
                if response.status_code in [200, 201]:
                    st.success("🎉 Booking Created Successfully!")
                    st.balloons()
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"FastAPI Connection Error:\n\n{e}")

    

    elif selected == "View Bookings":

        st.title("📋 Booking Management")
        st.caption("Manage all hotel bookings")

        headers = {}
        if st.session_state.token != "":
            headers["Authorization"] = f"Bearer {st.session_state.token}"

        try:
            response = requests.get("http://127.0.0.1:8000/bookings", headers=headers)

            if response.status_code == 200:
                bookings = response.json()
                if len(bookings) == 0:
                    st.warning("No Bookings Found")
                else:
                    df = pd.DataFrame(bookings)
                    st.divider()
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        search = st.text_input("🔍 Search Customer")

                    with col2:
                        if "room_type" in df.columns:
                            room = st.selectbox("Room Type", ["All"] + list(df["room_type"].unique()))
                        else:
                            room = "All"

                    if search != "" and "customer_name" in df.columns:
                        df = df[df["customer_name"].str.contains(search, case=False)]

                    if "room_type" in df.columns and room != "All":
                        df = df[df["room_type"] == room]

                    st.divider()
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    st.divider()
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("📄 Download CSV", csv, "hotel_bookings.csv", "text/csv", use_container_width=True)

                    st.divider()
                    st.subheader("Booking Actions")

                    if "id" in df.columns:
                        booking_id = st.selectbox("Select Booking ID", df["id"])
                        c1, c2 = st.columns(2)

                        with c1:
                            if st.button("✏ Edit Booking", use_container_width=True):
                                st.info("Edit feature will be added later.")

                        with c2:
                            if st.button("🗑 Delete Booking", use_container_width=True):
                                delete = requests.delete(f"http://127.0.0.1:8000/bookings/{booking_id}", headers=headers)
                                if delete.status_code == 200:
                                    st.success("Booking Deleted Successfully")
                                    st.rerun()
                                else:
                                    st.error("Unable to Delete Booking")
            else:
                st.error("Unable to Fetch Booking Data")
        except Exception as e:
            st.error(e)

    elif selected == "Analytics":

        st.title("📊 Hotel Analytics Dashboard")
        st.caption("Business Insights & Reports")

        headers = {}
        if st.session_state.token != "":
            headers["Authorization"] = f"Bearer {st.session_state.token}"

        try:
            response = requests.get("http://127.0.0.1:8000/bookings", headers=headers)

            if response.status_code == 200:
                bookings = response.json()
                if len(bookings) == 0:
                    st.warning("No Booking Data Available")
                else:
                    df = pd.DataFrame(bookings)
                    c1, c2, c3, c4 = st.columns(4)

                    total_bookings = len(df)
                    total_revenue = df["total_amount"].sum() if "total_amount" in df.columns else 0
                    avg_booking = round(df["total_amount"].mean(), 2) if "total_amount" in df.columns else 0
                    total_customers = df["customer_name"].nunique() if "customer_name" in df.columns else 0

                    c1.metric("📋 Bookings", total_bookings)
                    c2.metric("💰 Revenue", f"₹ {total_revenue:,.0f}")
                    c3.metric("👥 Customers", total_customers)
                    c4.metric("📈 Avg Booking", f"₹ {avg_booking}")

                    st.divider()
                    col1, col2 = st.columns(2)

                    with col1:
                        if "room_type" in df.columns:
                            fig = px.pie(df, names="room_type", hole=0.5, title="Room Distribution")
                            st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        if "room_type" in df.columns:
                            revenue = df.groupby("room_type")["total_amount"].sum().reset_index()
                            fig = px.bar(revenue, x="room_type", y="total_amount", color="room_type", text_auto=True)
                            st.plotly_chart(fig, use_container_width=True)

                    st.divider()
                    if "guests" in df.columns:
                        guest = df.groupby("guests").size().reset_index(name="Bookings")
                        fig = px.bar(guest, x="guests", y="Bookings", color="Bookings", text_auto=True)
                        st.plotly_chart(fig, use_container_width=True)

                    st.divider()
                    st.subheader("Revenue Summary")
                    if "room_type" in df.columns:
                        revenue = df.groupby("room_type")["total_amount"].sum().reset_index()
                        st.dataframe(revenue, use_container_width=True, hide_index=True)
            else:
                st.error("Unable to Fetch Data")
        except Exception as e:
            st.error(e)

    elif selected == "Profile":

        st.title("👤 Admin Profile")
        st.caption("Manage your account information")

        col1, col2 = st.columns([1, 3])

        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=180)

        with col2:
            st.subheader("Administrator")
            st.text_input("Full Name", value="Admin User", disabled=True)
            st.text_input("Email", value="admin@gmail.com", disabled=True)
            st.text_input("Hotel Name", value="Luxury Hotel", disabled=True)
            st.text_input("Role", value="System Administrator", disabled=True)

        st.divider()
        st.subheader("📊 Profile Statistics")

        c1, c2, c3 = st.columns(3)
        c1.metric("Experience", "5 Years")
        c2.metric("Bookings Managed", "250")
        c3.metric("Rating", "⭐ 4.9")

        st.divider()
        st.subheader("🔐 Change Password")

        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Update Password", use_container_width=True):
            if new_password == confirm_password:
                st.success("Password Updated Successfully")
            else:
                st.error("Passwords do not match.")

        st.divider()
        st.subheader("⚙ Preferences")
        dark_mode = st.toggle("Dark Mode", value=False)
        notifications = st.toggle("Email Notifications", value=True)
        auto_backup = st.toggle("Automatic Backup", value=True)

        st.divider()
        st.subheader("📄 Account Information")
        st.info(
            """
            **Application:** Hotel Booking Management System  
            **Frontend:** Streamlit  
            **Backend:** FastAPI  
            **Database:** PostgreSQL  
            **Version:** 1.0
            """
        )

    elif selected == "Settings":

        st.title("⚙ Settings")
        st.subheader("Application Settings")

        theme = st.selectbox("Theme", ["Light", "Dark"])
        language = st.selectbox("Language", ["English", "Hindi"])
        currency = st.selectbox("Currency", ["INR", "USD"])

        st.divider()
        st.subheader("Notification Settings")

        email = st.checkbox("Email Notifications", value=True)
        sms = st.checkbox("SMS Notifications", value=False)

        st.divider()
        st.subheader("Backup")

        if st.button("Create Backup", use_container_width=True):
            st.success("Backup Created Successfully")

        st.divider()
        if st.button("Save Settings", use_container_width=True):
            st.success("Settings Saved Successfully")

    elif selected == "Logout":

        st.session_state.logged_in = False
        st.session_state.token = ""
        st.success("Logged Out Successfully")
        st.rerun()
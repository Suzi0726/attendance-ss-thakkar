import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import os
import math

# CONFIGURATION
office_lat = 22.957421768359637
office_lon = 72.65552843722682
allowed_distance = 100
employees = ["CASHENAL", "SUJAL", "CAHEENA", "SONALI", "SHEFALI", "SAPNA"]
admin_key = "CASHENAL"

st.set_page_config(page_title="S S Thakkar & Co. Attendance", layout="centered")
st.title("🧾 S S THAKKAR & CO. ATTENDANCE")

query_params = st.query_params
is_admin = query_params.get("admin", "") == admin_key
staff_name = query_params.get("staff", "").upper() if not is_admin else ""

# GPS output area
st.markdown("### 📍 Click below to share your location")
clicked = st.button("📍 Share My Location")

# JS injection will only trigger when button is clicked
if clicked:
    components.html("""
    <script>
    navigator.geolocation.getCurrentPosition(function(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const coords = lat + "," + lon;
        const input = window.parent.document.querySelector('input[id="gps-data"]');
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, coords);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    });
    </script>
    """, height=0)

# Hidden field that JS writes into
gps = st.text_input("Current Location", key="gps-data", label_visibility="collapsed")

# Check and parse GPS
if gps:
    try:
        user_lat, user_lon = map(float, gps.split(","))
        st.success(f"📍 Location Shared: {user_lat:.5f}, {user_lon:.5f}")
    except:
        st.error("Failed to detect valid GPS coordinates.")
        st.stop()
else:
    st.info("Waiting for location... Click the button above.")
    st.stop()

# Calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

distance = haversine(user_lat, user_lon, office_lat, office_lon)

# Load and save attendance
log_file = "attendance_log.xlsx"
photo_folder = "photos"
os.makedirs(photo_folder, exist_ok=True)

def load_attendance():
    if os.path.exists(log_file):
        return pd.read_excel(log_file)
    else:
        return pd.DataFrame(columns=["Name", "Action", "Time", "Latitude", "Longitude", "Photo File", "Status"])

def save_attendance(df):
    df.to_excel(log_file, index=False)

df = load_attendance()

# Admin panel
if is_admin:
    st.header("🔐 Admin Panel")
    filter_name = st.selectbox("Filter by Employee", ["ALL"] + employees)
    today = datetime.now().strftime("%Y-%m-%d")
    view_df = df[df["Time"].astype(str).str.startswith(today)]
    if filter_name != "ALL":
        view_df = view_df[view_df["Name"] == filter_name]
    st.dataframe(view_df)
    csv_data = view_df.to_csv(index=False)
    file_name = f"{filter_name}_attendance.csv" if filter_name != "ALL" else "today_attendance.csv"
    st.download_button("📥 Download", data=csv_data, file_name=file_name, mime="text/csv")
    st.stop()

# Validate employee
if staff_name not in employees:
    st.error("Invalid or missing staff link.")
    st.stop()

# Show staff view
st.subheader(f"👋 Welcome, {staff_name}")
st.info(f"📏 Distance from office: {int(distance)} meters")

if distance > allowed_distance:
    st.error("❌ You are outside the 100 meter office boundary.")
    st.stop()

# Check today's attendance
today_str = datetime.now().strftime("%Y-%m-%d")
records_today = df[(df["Name"] == staff_name) & (df["Time"].astype(str).str.startswith(today_str))]
punch_in_done = any(records_today["Action"] == "Punch In")
punch_out_done = any(records_today["Action"] == "Punch Out")

if punch_in_done:
    st.success("✅ You already punched in today.")
if punch_out_done:
    st.success("✅ You already punched out today.")
if punch_in_done and punch_out_done:
    st.warning("✔️ You have completed both actions for today.")
    st.stop()

# Attendance form
with st.form("attendance_form"):
    st.success("📍 Location verified.")
    action = st.radio("Select Action:", ["Punch In", "Punch Out"], disabled=(punch_in_done, punch_out_done))
    photo = st.camera_input("📸 Click a selfie (required)")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not photo:
            st.error("❌ Photo is mandatory.")
            st.stop()

        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        photo_filename = f"{staff_name}-{today_str}-{action.replace(' ', '_').lower()}.jpg"
        photo_path = os.path.join(photo_folder, photo_filename)
        with open(photo_path, "wb") as f:
            f.write(photo.getbuffer())

        df = df.append({
            "Name": staff_name,
            "Action": action,
            "Time": time_now,
            "Latitude": user_lat,
            "Longitude": user_lon,
            "Photo File": photo_filename,
            "Status": "✅ Complete" if (action == "Punch Out" and punch_in_done) else "✅ Incomplete"
        }, ignore_index=True)

        save_attendance(df)
        st.success(f"✅ {action} recorded at {time_now}")


import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import os
import math

# CONFIGURATION
office_lat = 23.010455037590273
office_lon = 72.62062765767143
allowed_distance = 100
employees = ["CASHENAL", "SUJAL", "CAHEENA", "SONALI", "SHEFALI", "SAPNA"]
admin_key = "CASHENAL"

st.set_page_config(page_title="📍 S S Thakkar & Co. Attendance", layout="centered")
st.title("🗞 S S THAKKAR & CO. ATTENDANCE")

query_params = st.query_params
is_admin = query_params.get("admin", "") == admin_key
staff_name = query_params.get("staff", "").upper() if not is_admin else ""

location_output = st.empty()
gps_input = st.text_input("", key="gps-data", label_visibility="collapsed", disabled=True)

with location_output.container():
    components.html("""
    <div style='text-align:center;'>
        <button onclick="checkDistance()" style='padding: 10px 20px; font-size:16px;'>📍 Share My Location</button>
        <p id="result" style="margin-top: 20px; font-size: 18px;"></p>
    </div>
    <script>
    function getDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    function checkDistance() {
        navigator.geolocation.getCurrentPosition(function(position) {
            const userLat = position.coords.latitude;
            const userLon = position.coords.longitude;
            const officeLat = 23.010455037590273;
            const officeLon = 72.62062765767143;
            const dist = getDistance(userLat, userLon, officeLat, officeLon);
            const result = document.getElementById("result");

            if (dist <= 100) {
                result.innerHTML = `✅ Allowed (Distance: ${Math.round(dist)} meters)`;
                result.style.color = "green";
                const input = window.parent.document.querySelector('input[id="gps-data"]');
                const coords = userLat + "," + userLon;
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                nativeInputValueSetter.call(input, coords);
                input.dispatchEvent(new Event('input', { bubbles: true }));
            } else {
                result.innerHTML = `❌ Not Allowed (Distance: ${Math.round(dist)} meters)`;
                result.style.color = "red";
            }
        });
    }
    </script>
    """, height=300)

if not gps_input:
    st.warning("📍 Please click the location button to begin.")
    st.stop()

try:
    user_lat, user_lon = map(float, gps_input.split(","))
except:
    st.error("❌ Failed to get valid location.")
    st.stop()

log_file = "attendance_log.xlsx"
photo_folder = "photos"
os.makedirs(photo_folder, exist_ok=True)

def load_attendance():
    return pd.read_excel(log_file) if os.path.exists(log_file) else pd.DataFrame(columns=["Name", "Action", "Time", "Latitude", "Longitude", "Photo File", "Status"])

def save_attendance(df):
    df.to_excel(log_file, index=False)

df = load_attendance()

if is_admin:
    st.header("🔐 Admin Panel")
    emp_filter = st.selectbox("Filter by Employee", ["ALL"] + employees)
    today = datetime.now().strftime("%Y-%m-%d")
    filtered = df[df["Time"].astype(str).str.startswith(today)]
    if emp_filter != "ALL":
        filtered = filtered[filtered["Name"] == emp_filter]
    st.dataframe(filtered)
    st.download_button("📥 Download Report", filtered.to_csv(index=False), file_name=f"{emp_filter}_report.csv", mime="text/csv")
    st.stop()

if staff_name not in employees:
    st.error("Invalid or missing staff name in URL.")
    st.stop()

st.subheader(f"👋 Welcome, {staff_name}")
today_str = datetime.now().strftime("%Y-%m-%d")
records_today = df[(df["Name"] == staff_name) & (df["Time"].astype(str).str.startswith(today_str))]
punch_in_done = any(records_today["Action"] == "Punch In")
punch_out_done = any(records_today["Action"] == "Punch Out")

if punch_in_done and punch_out_done:
    st.success("✅ You have completed both actions for today.")
    st.stop()

with st.form("attendance_form"):
    st.success("📍 Location verified & allowed")
    action = st.radio("Choose Action", ["Punch In", "Punch Out"], disabled=(punch_in_done, punch_out_done))
    photo = st.camera_input("📸 Take a selfie (required)")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not photo:
            st.error("❌ Selfie is required.")
            st.stop()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        photo_filename = f"{staff_name}_{action.replace(' ', '_')}_{today_str}.jpg"
        photo_path = os.path.join(photo_folder, photo_filename)
        with open(photo_path, "wb") as f:
            f.write(photo.getbuffer())
        new_status = "✅ Complete" if (action == "Punch Out" and punch_in_done) else "✅ Incomplete"
        new_row = {
            "Name": staff_name,
            "Action": action,
            "Time": time_now,
            "Latitude": user_lat,
            "Longitude": user_lon,
            "Photo File": photo_filename,
            "Status": new_status
        }
        df = df.append(new_row, ignore_index=True)
        save_attendance(df)
        st.success(f"✅ {action} submitted successfully at {time_now}")

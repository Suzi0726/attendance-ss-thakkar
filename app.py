
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import os
import math

office_lat = 22.957531430064837
office_lon = 72.65531222328558
allowed_distance = 100
employees = ["CASHENAL", "SUJAL", "CAHEENA", "SONALI", "SHEFALI", "SAPNA"]
admin_key = "CASHENAL"

st.set_page_config(page_title="📍 Attendance", layout="centered")
st.title("🗞 S S THAKKAR & CO. ATTENDANCE")

query_params = st.query_params
is_admin = query_params.get("admin", "") == admin_key
staff_name = query_params.get("staff", "").upper() if not is_admin else ""

gps_input = st.text_input("", key="gps-data", label_visibility="collapsed", disabled=True)
components.html(r"""
<div style='text-align:center;'>
    <button onclick="getLocation()" style='padding:10px 20px;'>📍 Share My Location</button>
    <p id='result'></p>
</div>
<script>
function getLocation() {
    navigator.geolocation.getCurrentPosition(function(pos) {
        let lat = pos.coords.latitude;
        let lon = pos.coords.longitude;
        let dist = getDistance(lat, lon, 22.957531430064837, 72.65531222328558);
        document.getElementById('result').innerText = dist <= 100 ? "✅ Within range" : "❌ Too far";
        if (dist <= 100) {
            let input = window.parent.document.querySelector('input[id=\"gps-data\"]');
            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            setter.call(input, lat + "," + lon);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    });
}

function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000;
    const dLat = (lat2-lat1)*Math.PI/180;
    const dLon = (lon2-lon1)*Math.PI/180;
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}
</script>
""", height=280)

if not gps_input:
    st.warning("📍 Please share your location to continue.")
    st.stop()

try:
    user_lat, user_lon = map(float, gps_input.split(","))
except:
    st.error("❌ Invalid location.")
    st.stop()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

if haversine(user_lat, user_lon, office_lat, office_lon) > allowed_distance:
    st.error("❌ You are not at the office.")
    st.stop()

if staff_name not in employees:
    st.error("🚫 Invalid staff name in URL.")
    st.stop()

log_file = "attendance_log.xlsx"
photo_folder = "photos"
os.makedirs(photo_folder, exist_ok=True)

df = pd.read_excel(log_file) if os.path.exists(log_file) else pd.DataFrame(columns=["Name","Action","Time","Latitude","Longitude","Photo","Status"])
today = datetime.now().strftime("%Y-%m-%d")
records_today = df[(df["Name"] == staff_name) & (df["Time"].str.startswith(today))]

in_done = any(records_today["Action"] == "Punch In")
out_done = any(records_today["Action"] == "Punch Out")

if in_done and out_done:
    st.success("✅ Both actions already completed.")
    st.stop()

with st.form("attendance"):
    st.success("📍 Location confirmed.")
    action = st.radio("Select Action", ["Punch In", "Punch Out"], disabled=(in_done and not out_done))
    photo = st.camera_input("📸 Required Selfie")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not photo:
            st.error("❌ Selfie is required.")
            st.stop()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        photo_file = f"{staff_name}_{action.replace(' ','_')}_{today}.jpg"
        with open(os.path.join(photo_folder, photo_file), "wb") as f:
            f.write(photo.getbuffer())
        df = pd.concat([df, pd.DataFrame([{
            "Name": staff_name, "Action": action, "Time": now,
            "Latitude": user_lat, "Longitude": user_lon,
            "Photo": photo_file, "Status": "✅"
        }])])
        df.to_excel(log_file, index=False)
        st.success(f"✅ {action} recorded at {now}")

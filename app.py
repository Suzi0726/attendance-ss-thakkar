# GPS Attendance System with Share Button
# NOTE: This script requires Streamlit to be installed locally to run properly.

try:
    import streamlit as st
    import streamlit.components.v1 as components
    from datetime import datetime
    import pandas as pd
    import os
    import math
except ModuleNotFoundError:
    print("This script must be run in an environment with Streamlit installed. Please install Streamlit using 'pip install streamlit' and run with 'streamlit run app.py'")
    exit()

# CONFIGURATION
office_lat = 22.957421768359637
office_lon = 72.65552843722682
allowed_distance = 100
employees = ["CASHENAL", "SUJAL", "CAHEENA", "SONALI", "SHEFALI", "SAPNA"]
admin_key = "CASHENAL"

st.set_page_config(page_title="📍 S S Thakkar & Co. Attendance", layout="centered")
st.title("🗞 S S THAKKAR & CO. ATTENDANCE")

query_params = st.query_params
is_admin = query_params.get("admin", "") == admin_key
staff_name = query_params.get("staff", "").upper() if not is_admin else ""

# Inject HTML button + JS for GPS
gps_placeholder = st.empty()
gps_input = st.text_input("", key="gps-data", label_visibility="collapsed", disabled=True)

with gps_placeholder.container():
    components.html("""
    <div style='text-align:center;'>
        <button onclick="getLocation()" style='padding: 10px 20px; font-size:16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;'>📍 Share My Location</button>
    </div>
    <script>
    function getLocation() {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const coords = lat + "," + lon;
            const input = window.parent.document.querySelector('input[id="gps-data"]');
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeInputValueSetter.call(input, coords);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    }
    </script>
    """, height=0)

# Wait for location
if not gps_input:
    st.info("📍 Please click the Share Location button above to continue.")
    st.stop()

try:
    user_lat, user_lon = map(float, gps_input.split(","))
    st.success(f"📍 Location shared: {user_lat:.5f}, {user_lon:.5f}")
except:
    st.error("❌ Failed to read location.")
    st.stop()

# ... (rest of your logic: distance check, punch in/out form, photo, admin panel, etc.)

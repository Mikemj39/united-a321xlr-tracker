import streamlit as st
import pandas as pd
import requests
st.set_page_config(
    page_title="United A321XLR Fleet Tracker",
    page_icon="✈️",
    layout="wide"
)
# -------------------------
# FR24 Flight Summary Test - N64321
# -------------------------

from datetime import datetime, timedelta, timezone

fr24_token = st.secrets["FR24_API_TOKEN"]

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {fr24_token}",
    "Accept-Version": "v1"
}

# Search the last 24 hours
now = datetime.now(timezone.utc)
yesterday = now - timedelta(hours=24)

params = {
    "flight_datetime_from": yesterday.strftime("%Y-%m-%dT%H:%M:%S"),
    "flight_datetime_to": now.strftime("%Y-%m-%dT%H:%M:%S"),
    "registrations": "N64321",
    "limit": 20,
    "sort": "desc"
}

try:
    response = requests.get(
        "https://fr24api.flightradar24.com/api/flight-summary/full",
        headers=headers,
        params=params,
        timeout=10
    )

    if response.status_code == 200:
        fr24_data = response.json()
        flights = fr24_data.get("data", [])

        st.success(f"✈️ Found {len(flights)} N64321 flight(s) in the last 24 hours")

        for flight in flights:
            st.write("---")
            st.write("**Flight:**", flight.get("flight", "—"))
            st.write("**Registration:**", flight.get("reg", "—"))
            st.write("**Origin:**", flight.get("orig_iata", "—"))
            st.write("**Destination:**", flight.get("dest_iata", "—"))
            st.write("**Takeoff:**", flight.get("datetime_takeoff", "—"))
            st.write("**Landing:**", flight.get("datetime_landed", "—"))
            st.write("**Flight Time (seconds):**", flight.get("flight_time", "—"))
            st.write("**Actual Distance (km):**", flight.get("actual_distance", "—"))
            st.write("**Flight Ended:**", flight.get("flight_ended", "—"))
            st.write("**FR24 ID:**", flight.get("fr24_id", "—"))

        with st.expander("View full Flight Summary response"):
            st.json(fr24_data)

    else:
        st.error(f"FR24 API error: {response.status_code}")
        st.code(response.text)

except requests.RequestException as e:
    st.error("Could not connect to the FR24 API.")
    st.code(str(e))
# -------------------------
# Load master fleet database
# -------------------------

fleet = pd.read_csv("fleet.csv")

# -------------------------
# Calculate fleet statistics
# -------------------------

total_order = 50
delivered = len(fleet[fleet["fleet_status"] == "Active"])
pre_delivery = len(fleet[fleet["fleet_status"] == "Pre-delivery"])
tracked = len(fleet)

# -------------------------
# Header
# -------------------------

st.title("✈️ United A321XLR Fleet Tracker")
st.caption("Tracking the United Airlines Airbus A321XLR fleet")

# -------------------------
# Fleet overview
# -------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("United XLR Order", total_order)
col2.metric("Delivered", delivered)
col3.metric("Pre-Delivery", pre_delivery)
col4.metric("Tracked Aircraft", tracked)

st.divider()

# -------------------------
# Prepare fleet table
# -------------------------

display_fleet = fleet[
    [
        "registration",
        "msn",
        "fleet_status",
        "location",
        "delivery_date",
        "test_registration",
        "notes"
    ]
].copy()

display_fleet.columns = [
    "Registration",
    "MSN",
    "Status",
    "Location",
    "Delivery Date",
    "Test Registration",
    "Notes"
]

# Replace blank values with —
display_fleet = display_fleet.fillna("—")

# -------------------------
# Fleet table
# -------------------------

st.subheader("Fleet Status")

st.dataframe(
    display_fleet,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.caption(
    "United A321XLR Fleet Tracker • Fleet database connected • Live flight data coming soon"
)

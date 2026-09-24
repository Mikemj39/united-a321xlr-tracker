import streamlit as st
import pandas as pd
import requests
st.set_page_config(
    page_title="United A321XLR Fleet Tracker",
    page_icon="✈️",
    layout="wide"
)
# -------------------------
# FR24 Production Test - N64321
# -------------------------

fr24_token = st.secrets["FR24_API_TOKEN"]

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {fr24_token}",
    "Accept-Version": "v1"
}

try:
    response = requests.get(
        "https://fr24api.flightradar24.com/api/live/flight-positions/full",
        headers=headers,
        params={"registrations": "N64321"},
        timeout=10
    )

    if response.status_code == 200:
        fr24_data = response.json()
        flights = fr24_data.get("data", [])

        if flights:
            flight = flights[0]

            st.success("✈️ N64321 found on FR24!")

            st.write("**Flight:**", flight.get("flight", "—"))
            st.write("**Registration:**", flight.get("reg", "—"))
            st.write("**Origin:**", flight.get("orig_iata", "—"))
            st.write("**Destination:**", flight.get("dest_iata", "—"))
            st.write("**FR24 Flight ID:**", flight.get("fr24_id", "—"))

            with st.expander("View full FR24 response"):
                st.json(fr24_data)

        else:
            st.info("N64321 is not currently appearing as an active flight on FR24.")

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

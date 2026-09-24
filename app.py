import streamlit as st
import pandas as pd
import requests
st.set_page_config(
    page_title="United A321XLR Fleet Tracker",
    page_icon="✈️",
    layout="wide"
)
# -------------------------
# FR24 Sandbox Test
# -------------------------

sandbox_token = st.secrets["FR24_SANDBOX_TOKEN"]

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {sandbox_token}",
    "Accept-Version": "v1"
}

try:
    sandbox_response = requests.get(
        "https://fr24api.flightradar24.com/api/live/flight-positions/full",
        headers=headers,
        params={"registration": "N64321"},
        timeout=10
    )

    if sandbox_response.status_code == 200:
        sandbox_data = sandbox_response.json()

        st.success("🧪 FR24 Sandbox connected successfully!")

        with st.expander("View sandbox API response"):
            st.json(sandbox_data)

    else:
        st.error(
            f"FR24 Sandbox error: {sandbox_response.status_code}"
        )
        st.code(sandbox_response.text)

except requests.RequestException as e:
    st.error("Could not connect to the FR24 Sandbox.")
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

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="United A321XLR Fleet Tracker",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ United A321XLR Fleet Tracker")
st.caption("Tracking the United Airlines Airbus A321XLR fleet")

# -------------------------
# Fleet data
# -------------------------

fleet = [
    {
        "Registration": "N64321",
        "MSN": "12581",
        "Status": "Active",
        "Location": "Tracking coming soon",
        "Flight": "—",
        "Route": "—"
    },
    {
        "Registration": "N64322",
        "MSN": "12820",
        "Status": "Pre-delivery",
        "Location": "XFW",
        "Flight": "—",
        "Route": "—"
    },
    {
        "Registration": "N54323",
        "MSN": "12979",
        "Status": "Pre-delivery",
        "Location": "XFW",
        "Flight": "—",
        "Route": "—"
    }
]

df = pd.DataFrame(fleet)

# -------------------------
# Fleet overview
# -------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("United XLR Order", "50")
col2.metric("Delivered", "1")
col3.metric("Pre-Delivery", "2")
col4.metric("Tracked Aircraft", len(df))

st.divider()

# -------------------------
# Fleet table
# -------------------------

st.subheader("Fleet Status")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.caption("United A321XLR Fleet Tracker • Data integration coming soon")

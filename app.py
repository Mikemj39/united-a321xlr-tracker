import streamlit as st
import pandas as pd
from supabase import create_client


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="United A321XLR Fleet Tracker",
    page_icon="✈️",
    layout="wide"
)


# --------------------------------------------------
# Supabase Connection
# --------------------------------------------------

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

try:
    flight_response = (
        supabase
        .table("flights")
        .select("*")
        .order("takeoff_time", desc=True)
        .execute()
    )

    flights = pd.DataFrame(flight_response.data)

except Exception as e:
    st.error("Could not load flight data.")
    st.code(str(e))
    flights = pd.DataFrame()


# --------------------------------------------------
# Load Master Fleet Database
# --------------------------------------------------

fleet = pd.read_csv("fleet.csv")


# --------------------------------------------------
# Calculate Fleet Statistics
# --------------------------------------------------

total_order = 50
delivered = len(fleet[fleet["fleet_status"] == "Active"])
pre_delivery = len(fleet[fleet["fleet_status"] == "Pre-delivery"])
tracked = len(fleet)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("✈️ United A321XLR Fleet Tracker")
st.caption("Tracking the United Airlines Airbus A321XLR fleet")


# --------------------------------------------------
# Fleet Overview
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("United XLR Order", total_order)
col2.metric("Delivered", delivered)
col3.metric("Pre-Delivery", pre_delivery)
col4.metric("Tracked Aircraft", tracked)

st.divider()


# --------------------------------------------------
# Prepare Fleet Table
# --------------------------------------------------

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

display_fleet = display_fleet.fillna("—")


# --------------------------------------------------
# N64321 Flight Statistics
# --------------------------------------------------

st.subheader("N64321 Flight Statistics")

if not flights.empty and "registration" in flights.columns:

    xlr_flights = flights[
        flights["registration"] == "N64321"
    ].copy()

else:
    xlr_flights = pd.DataFrame()


if not xlr_flights.empty:

    # Convert FR24 kilometers to miles
    xlr_flights["distance_miles"] = (
        pd.to_numeric(
            xlr_flights["distance_km"],
            errors="coerce"
        ) * 0.621371
    )

    # Convert FR24 seconds to hours
    xlr_flights["flight_hours"] = (
        pd.to_numeric(
            xlr_flights["flight_time_seconds"],
            errors="coerce"
        ) / 3600
    )

    # Calculate statistics
    total_flights = len(xlr_flights)
    total_miles = xlr_flights["distance_miles"].sum()
    total_hours = xlr_flights["flight_hours"].sum()
    average_miles = xlr_flights["distance_miles"].mean()
    average_hours = xlr_flights["flight_hours"].mean()

    # Display statistics
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Flights",
        f"{total_flights:,}"
    )

    col2.metric(
        "Total Miles",
        f"{total_miles:,.0f}"
    )

    col3.metric(
        "Flight Hours",
        f"{total_hours:,.1f}"
    )

    col4.metric(
        "Avg Distance",
        f"{average_miles:,.0f} mi"
    )

    col5.metric(
        "Avg Duration",
        f"{average_hours:.1f} hrs"
    )

    st.divider()


    # --------------------------------------------------
    # Collapsible Flight Log
    # --------------------------------------------------

    with st.expander(
        f"✈️ View N64321 Flight Log ({total_flights} flights)"
    ):

        # Convert timestamps
        xlr_flights["takeoff_time"] = pd.to_datetime(
            xlr_flights["takeoff_time"],
            errors="coerce"
        )

        xlr_flights["landing_time"] = pd.to_datetime(
            xlr_flights["landing_time"],
            errors="coerce"
        )

        # Format flight duration
        def format_duration(seconds):

            if pd.isna(seconds):
                return "—"

            seconds = int(seconds)

            hours = seconds // 3600
            minutes = (seconds % 3600) // 60

            return f"{hours}h {minutes}m"


        xlr_flights["Duration"] = (
            xlr_flights["flight_time_seconds"]
            .apply(format_duration)
        )

        # Format distance
        xlr_flights["Distance"] = (
            xlr_flights["distance_miles"]
            .apply(
                lambda x:
                f"{x:,.0f} mi"
                if pd.notna(x)
                else "—"
            )
        )

        # Build flight log
        flight_log = xlr_flights[
            [
                "takeoff_time",
                "flight_number",
                "origin",
                "destination",
                "Duration",
                "Distance"
            ]
        ].copy()

        flight_log.columns = [
            "Date / Takeoff",
            "Flight",
            "From",
            "To",
            "Duration",
            "Distance"
        ]

        # Display flight log
        st.dataframe(
            flight_log,
            use_container_width=True,
            hide_index=True
        )


else:

    st.info(
        "No completed flight records are currently stored for N64321."
    )


# --------------------------------------------------
# Fleet Table
# --------------------------------------------------

st.divider()

st.subheader("Fleet Status")

st.dataframe(
    display_fleet,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "United A321XLR Fleet Tracker • "
    "Fleet database connected • "
    "Flight statistics powered by stored flight records"
)

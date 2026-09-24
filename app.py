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
# Helper Functions
# --------------------------------------------------

def format_duration(seconds):
    if pd.isna(seconds):
        return "—"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    return f"{hours}h {minutes}m"


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

# Delivered includes aircraft already in service
# plus aircraft handed over but not yet in revenue service.
delivered = len(
    fleet[
        fleet["fleet_status"].isin(
            ["Delivered", "Active"]
        )
    ]
)

# In Service includes only aircraft currently active.
active = len(
    fleet[
        fleet["fleet_status"] == "Active"
    ]
)

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
col3.metric("In Service", active)
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
        "entry_into_service",
        "test_registration",
        "notes"
    ]
].copy()


# Start with manually stored location from fleet.csv.
# This is used for aircraft that do not yet have
# operational flight records in Supabase.
display_fleet["current_location"] = display_fleet["location"]

# Aircraft without operational flight records
# start with no last flight.
display_fleet["last_flight"] = "—"


# --------------------------------------------------
# Add Dynamic Flight Information to Fleet Table
# --------------------------------------------------

if not flights.empty and "registration" in flights.columns:

    fleet_flights = flights.copy()

    fleet_flights["takeoff_time"] = pd.to_datetime(
        fleet_flights["takeoff_time"],
        errors="coerce",
        utc=True
    )

    # Newest flights first
    fleet_flights = fleet_flights.sort_values(
        "takeoff_time",
        ascending=False
    )

    # Keep newest completed flight for each aircraft
    latest_flights = (
        fleet_flights
        .dropna(subset=["registration"])
        .drop_duplicates(
            subset=["registration"],
            keep="first"
        )
    )

    for _, latest in latest_flights.iterrows():

        registration = latest.get("registration")
        destination = latest.get("destination")
        origin = latest.get("origin")
        flight_number = latest.get("flight_number")

        aircraft_match = (
            display_fleet["registration"] == registration
        )

        # Destination of latest completed flight
        # becomes current known airport.
        if pd.notna(destination):

            display_fleet.loc[
                aircraft_match,
                "current_location"
            ] = destination

        # Build last-flight description.
        if (
            pd.notna(flight_number)
            and pd.notna(origin)
            and pd.notna(destination)
        ):

            last_flight_text = (
                f"{flight_number} "
                f"{origin} → {destination}"
            )

            display_fleet.loc[
                aircraft_match,
                "last_flight"
            ] = last_flight_text


# --------------------------------------------------
# Build Final Fleet Display Table
# --------------------------------------------------

display_fleet = display_fleet[
    [
        "registration",
        "msn",
        "fleet_status",
        "current_location",
        "delivery_date",
        "entry_into_service",
        "test_registration",
        "last_flight",
        "notes"
    ]
].copy()

display_fleet.columns = [
    "Registration",
    "MSN",
    "Status",
    "Current Location",
    "Delivery Date",
    "Entry Into Service",
    "Test Registration",
    "Last Flight",
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

    # --------------------------------------------------
    # Prepare Flight Data
    # --------------------------------------------------

    xlr_flights["distance_miles"] = (
        pd.to_numeric(
            xlr_flights["distance_km"],
            errors="coerce"
        ) * 0.621371
    )

    xlr_flights["flight_time_seconds"] = pd.to_numeric(
        xlr_flights["flight_time_seconds"],
        errors="coerce"
    )

    xlr_flights["flight_hours"] = (
        xlr_flights["flight_time_seconds"] / 3600
    )

    xlr_flights["takeoff_time"] = pd.to_datetime(
        xlr_flights["takeoff_time"],
        errors="coerce",
        utc=True
    )

    xlr_flights["landing_time"] = pd.to_datetime(
        xlr_flights["landing_time"],
        errors="coerce",
        utc=True
    )

    xlr_flights["route"] = (
        xlr_flights["origin"].fillna("—")
        + " → "
        + xlr_flights["destination"].fillna("—")
    )


    # --------------------------------------------------
    # Main Statistics
    # --------------------------------------------------

    total_flights = len(xlr_flights)

    total_miles = xlr_flights[
        "distance_miles"
    ].sum()

    total_hours = xlr_flights[
        "flight_hours"
    ].sum()

    average_miles = xlr_flights[
        "distance_miles"
    ].mean()

    average_seconds = xlr_flights[
        "flight_time_seconds"
    ].mean()


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
        format_duration(average_seconds)
    )


    # --------------------------------------------------
    # Detailed Statistics
    # --------------------------------------------------

    st.markdown("### Aircraft Records")

    # Longest flight by distance
    longest_distance_row = xlr_flights.loc[
        xlr_flights["distance_miles"].idxmax()
    ]

    longest_distance = longest_distance_row[
        "distance_miles"
    ]

    longest_distance_route = longest_distance_row[
        "route"
    ]

    # Longest flight by duration
    longest_time_row = xlr_flights.loc[
        xlr_flights["flight_time_seconds"].idxmax()
    ]

    longest_time = longest_time_row[
        "flight_time_seconds"
    ]

    longest_time_route = longest_time_row[
        "route"
    ]

    # Most-flown route
    route_counts = xlr_flights[
        "route"
    ].value_counts()

    most_flown_route = route_counts.index[0]
    most_flown_route_count = route_counts.iloc[0]

    # Airports visited
    airports = pd.concat(
        [
            xlr_flights["origin"],
            xlr_flights["destination"]
        ]
    ).dropna().unique()

    airports_visited = len(airports)

    # Most recent flight
    latest_flight = xlr_flights.sort_values(
        "takeoff_time",
        ascending=False
    ).iloc[0]

    latest_flight_number = latest_flight[
        "flight_number"
    ]

    latest_route = latest_flight[
        "route"
    ]

    # Current airport = destination of
    # most recent completed flight.
    current_airport = latest_flight[
        "destination"
    ]


    # --------------------------------------------------
    # Aircraft Record Metrics
    # --------------------------------------------------

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric(
        "Longest Flight",
        f"{longest_distance:,.0f} mi",
        longest_distance_route
    )

    col2.metric(
        "Longest Duration",
        format_duration(longest_time),
        longest_time_route
    )

    col3.metric(
        "Most-Flown Route",
        most_flown_route,
        f"{most_flown_route_count} flights"
    )

    col4.metric(
        "Airports Visited",
        airports_visited
    )

    col5.metric(
        "Current Airport",
        current_airport
    )

    col6.metric(
        "Last Flight",
        latest_flight_number,
        latest_route
    )

    st.divider()


    # --------------------------------------------------
    # Route Statistics
    # --------------------------------------------------

    with st.expander("🛫 View Route Statistics"):

        route_stats = (
            xlr_flights
            .groupby(
                ["origin", "destination"],
                dropna=False
            )
            .agg(
                Flights=("fr24_id", "count"),
                Total_Miles=("distance_miles", "sum"),
                Avg_Miles=("distance_miles", "mean"),
                Avg_Duration_Seconds=(
                    "flight_time_seconds",
                    "mean"
                )
            )
            .reset_index()
        )

        route_stats["Route"] = (
            route_stats["origin"].fillna("—")
            + " → "
            + route_stats["destination"].fillna("—")
        )

        route_stats["Total Miles"] = (
            route_stats["Total_Miles"]
            .apply(
                lambda x:
                f"{x:,.0f} mi"
                if pd.notna(x)
                else "—"
            )
        )

        route_stats["Avg Distance"] = (
            route_stats["Avg_Miles"]
            .apply(
                lambda x:
                f"{x:,.0f} mi"
                if pd.notna(x)
                else "—"
            )
        )

        route_stats["Avg Duration"] = (
            route_stats["Avg_Duration_Seconds"]
            .apply(format_duration)
        )

        route_display = route_stats[
            [
                "Route",
                "Flights",
                "Total Miles",
                "Avg Distance",
                "Avg Duration"
            ]
        ].sort_values(
            "Flights",
            ascending=False
        )

        st.dataframe(
            route_display,
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------
    # Flight Log
    # --------------------------------------------------

    with st.expander(
        f"✈️ View N64321 Flight Log ({total_flights} flights)"
    ):

        xlr_flights["Duration"] = (
            xlr_flights[
                "flight_time_seconds"
            ].apply(format_duration)
        )

        xlr_flights["Distance"] = (
            xlr_flights[
                "distance_miles"
            ].apply(
                lambda x:
                f"{x:,.0f} mi"
                if pd.notna(x)
                else "—"
            )
        )

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

        flight_log = flight_log.sort_values(
            "Date / Takeoff",
            ascending=False
        )

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
# Fleet Status
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

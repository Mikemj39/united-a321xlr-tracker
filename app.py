    # --------------------------------------------------
    # Detailed Statistics / Aircraft Records
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

    # Current airport
    # Destination of the most recent completed flight
    current_airport = latest_flight[
        "destination"
    ]

    # Aircraft record metrics
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

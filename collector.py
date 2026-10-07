import os
import requests
from datetime import datetime, timedelta, timezone
from supabase import create_client


# --------------------------------------------------
# Configuration
# --------------------------------------------------

REGISTRATIONS = [
    "N64321",
    "N64322",
]

# Look back far enough to catch flights that were still
# in progress during the previous day's collection.
LOOKBACK_HOURS = 30


# --------------------------------------------------
# Credentials
# --------------------------------------------------

FR24_API_TOKEN = os.environ["FR24_API_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# --------------------------------------------------
# Build Query Window
# --------------------------------------------------

now = datetime.now(timezone.utc)
window_start = now - timedelta(hours=LOOKBACK_HOURS)

date_from = window_start.strftime("%Y-%m-%dT%H:%M:%S")
date_to = now.strftime("%Y-%m-%dT%H:%M:%S")

print(
    f"Checking {', '.join(REGISTRATIONS)} from "
    f"{date_from} to {date_to} UTC"
)


# --------------------------------------------------
# Request FR24 Flight Summaries
# --------------------------------------------------

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {FR24_API_TOKEN}",
    "Accept-Version": "v1"
}

params = {
    "flight_datetime_from": date_from,
    "flight_datetime_to": date_to,
    "registrations": ",".join(REGISTRATIONS),
    "limit": 100,
    "sort": "asc"
}

response = requests.get(
    "https://fr24api.flightradar24.com/api/flight-summary/full",
    headers=headers,
    params=params,
    timeout=20
)

response.raise_for_status()

recent_flights = response.json().get("data", [])

print(f"FR24 returned {len(recent_flights)} flight records.")


# --------------------------------------------------
# Process Flights
# --------------------------------------------------

completed_found = 0
inserted = 0
duplicates = 0
in_progress = 0
invalid = 0


for flight in recent_flights:

    fr24_id = flight.get("fr24_id")
    flight_number = flight.get("flight")
    registration = flight.get("reg")
    origin = flight.get("orig_iata")
    destination = flight.get("dest_iata")

    # Only permanently store completed flights
    if flight.get("flight_ended") is not True:

        print(
            f"Skipping in-progress flight: "
            f"{registration} "
            f"{flight_number} "
            f"{origin} -> {destination}"
        )

        in_progress += 1
        continue

    completed_found += 1

    # Require a unique FR24 ID
    if not fr24_id:

        print(
            f"Skipping flight with no FR24 ID: "
            f"{registration} {flight_number}"
        )

        invalid += 1
        continue

    # Check whether the flight is already stored
    existing = (
        supabase
        .table("flights")
        .select("fr24_id")
        .eq("fr24_id", fr24_id)
        .execute()
    )

    if existing.data:

        print(
            f"Already stored: "
            f"{registration} "
            f"{flight_number} "
            f"{origin} -> {destination} "
            f"({fr24_id})"
        )

        duplicates += 1
        continue

    # Prepare new flight
    record = {
        "fr24_id": fr24_id,
        "registration": registration,
        "flight_number": flight_number,
        "origin": origin,
        "destination": destination,
        "takeoff_time": flight.get("datetime_takeoff"),
        "landing_time": flight.get("datetime_landed"),
        "flight_time_seconds": flight.get("flight_time"),
        "distance_km": flight.get("actual_distance")
    }

    # Store new flight
    supabase.table(
        "flights"
    ).insert(
        record
    ).execute()

    inserted += 1

    print(
        f"NEW FLIGHT STORED: "
        f"{registration} "
        f"{flight_number} "
        f"{origin} -> {destination} "
        f"({fr24_id})"
    )


# --------------------------------------------------
# Collection Summary
# --------------------------------------------------

print()
print("COLLECTION COMPLETE")
print("--------------------------------")
print(f"Aircraft:              {', '.join(REGISTRATIONS)}")
print(f"Lookback period:        {LOOKBACK_HOURS} hours")
print(f"FR24 records returned: {len(recent_flights)}")
print(f"Completed flights:     {completed_found}")
print(f"New flights inserted:  {inserted}")
print(f"Duplicates skipped:    {duplicates}")
print(f"In-progress skipped:   {in_progress}")
print(f"Invalid records:       {invalid}")
print(f"Collection finished:   {now.isoformat()}")

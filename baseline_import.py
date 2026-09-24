import os
import requests
from datetime import datetime, timezone
from supabase import create_client

# --------------------------------------------------
# Credentials
# --------------------------------------------------

FR24_API_TOKEN = os.environ["FR24_API_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------------------------------------
# FR24 request
# --------------------------------------------------

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {FR24_API_TOKEN}",
    "Accept-Version": "v1"
}

params = {
    "flight_datetime_from": "2026-09-11T00:00:00",
    "flight_datetime_to": datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S"
    ),
    "registrations": "N64321",
    "limit": 100,
    "sort": "asc"
}

print("Requesting N64321 service history from FR24...")

response = requests.get(
    "https://fr24api.flightradar24.com/api/flight-summary/full",
    headers=headers,
    params=params,
    timeout=20
)

response.raise_for_status()

flights = response.json().get("data", [])

print(f"FR24 returned {len(flights)} flight records.")

# --------------------------------------------------
# Import completed flights
# --------------------------------------------------

completed = 0
inserted = 0
skipped = 0

for flight in flights:

    # Never permanently import a flight until it has ended
    if flight.get("flight_ended") is not True:
        print(
            f"Skipping live flight: "
            f"{flight.get('flight')} / {flight.get('fr24_id')}"
        )
        continue

    completed += 1

    fr24_id = flight.get("fr24_id")

    if not fr24_id:
        print("Skipping record with no FR24 ID.")
        continue

    # Check whether we already have this flight
    existing = (
        supabase
        .table("flights")
        .select("fr24_id")
        .eq("fr24_id", fr24_id)
        .execute()
    )

    if existing.data:
        print(f"Already stored: {fr24_id}")
        skipped += 1
        continue

    record = {
        "fr24_id": fr24_id,
        "registration": flight.get("reg"),
        "flight_number": flight.get("flight"),
        "origin": flight.get("orig_iata"),
        "destination": flight.get("dest_iata"),
        "takeoff_time": flight.get("datetime_takeoff"),
        "landing_time": flight.get("datetime_landed"),
        "flight_time_seconds": flight.get("flight_time"),
        "distance_km": flight.get("actual_distance")
    }

    supabase.table("flights").insert(record).execute()

    inserted += 1

    print(
        f"Imported: {record['flight_number']} "
        f"{record['origin']} -> {record['destination']} "
        f"({fr24_id})"
    )

# --------------------------------------------------
# Results
# --------------------------------------------------

print()
print("BASELINE IMPORT COMPLETE")
print("------------------------")
print(f"FR24 records returned: {len(flights)}")
print(f"Completed flights:      {completed}")
print(f"New flights inserted:   {inserted}")
print(f"Duplicates skipped:     {skipped}")

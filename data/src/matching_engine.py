"""Loads records and volunteer input."""
import csv
import json
from typing import Dict, List, Optional

from models import Opportunity, Volunteer, requirement_codes


def load_opportunities(path: str) -> List[Opportunity]:
    opportunities = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            distance = row["distance_miles"].strip()
            opportunities.append(Opportunity(
                id=row["id"],
                name=row["name"],
                activity=row["activity"],
                day=row["day"],
                time_of_day=row["time_of_day"],
                mode=row["mode"],
                distance_miles=float(distance) if distance else None,
                requirement_text=row["requirement"],
                requirements=requirement_codes(row["requirement"]),
            ))
    return opportunities


def volunteer_from_dict(d: Dict) -> Volunteer:
    return Volunteer(
        interests_text=d["interests_text"],
        availability_days=d["availability_days"],
        availability_times=d["availability_times"],
        willing_online=bool(d["willing_online"]),
        willing_in_person=bool(d["willing_in_person"]),
        max_travel_miles=d.get("max_travel_miles"),
        clearances=d.get("clearances", {}),
    )


def load_volunteer(path: str, overrides: Optional[Dict] = None) -> Volunteer:
    """Load a volunteer JSON file, optionally overriding fields to test changed inputs."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data.update(overrides or {})
    return volunteer_from_dict(data)
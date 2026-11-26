"""Shared builders for tests."""
from models import Opportunity, Volunteer

DEFAULT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def volunteer(**overrides):
    fields = dict(
        interests_text="",
        availability_days=DEFAULT_DAYS,
        availability_times=["evening"],
        willing_online=True,
        willing_in_person=True,
        max_travel_miles=3,
        clearances={},
    )
    fields.update(overrides)
    return Volunteer(**fields)


def opportunity(**overrides):
    fields = dict(
        id="test-role",
        name="Test role",
        activity="",
        day="Wed",
        time_of_day="evening",
        mode="in_person",
        distance_miles=1.0,
        requirement_text="None listed",
        requirements=[],
    )
    fields.update(overrides)
    return Opportunity(**fields)


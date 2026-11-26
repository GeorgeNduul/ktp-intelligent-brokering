"""Hard-constraint checks.

A FAIL excludes a role. An UNKNOWN leaves it unconfirmed. Missing facts are
never assumed to pass.
"""
from typing import List

from models import FAIL, PASS, REQUIREMENT_LABELS, UNKNOWN, Check, Opportunity, Volunteer


def check_availability(v: Volunteer, o: Opportunity) -> Check:
    when = f"{o.day} {o.time_of_day}"
    if o.day in v.availability_days and o.time_of_day in v.availability_times:
        return Check("availability", PASS, f"{when} fits your availability")
    return Check("availability", FAIL, f"{when} is outside your availability")


def check_mode(v: Volunteer, o: Opportunity) -> Check:
    online = o.mode == "online"
    allowed = v.willing_online if online else v.willing_in_person
    offered = "online" if online else "in person"
    if allowed:
        return Check("mode", PASS, f"Offered {offered}, which you are willing to do")
    return Check("mode", FAIL, f"Offered {offered}, which you have said you cannot do")


def check_distance(v: Volunteer, o: Opportunity) -> Check:
    if o.mode == "online":
        return Check("distance", PASS, "Online role, so the travel limit does not apply")
    if v.max_travel_miles is None:
        return Check("distance", UNKNOWN, "Your travel limit is not recorded; confirm it before referring")
    if o.distance_miles is None:
        return Check(
            "distance", UNKNOWN,
            f"Distance is not recorded for this in-person role; confirm it is within "
            f"{v.max_travel_miles:g} miles before referring",
        )
    unit = "mile" if o.distance_miles == 1 else "miles"
    if o.distance_miles <= v.max_travel_miles:
        return Check("distance", PASS,
                     f"{o.distance_miles:g} {unit}, within your {v.max_travel_miles:g}-mile limit")
    return Check("distance", FAIL,
                 f"{o.distance_miles:g} {unit}, beyond your {v.max_travel_miles:g}-mile limit")


def check_requirements(v: Volunteer, o: Opportunity) -> List[Check]:
    if not o.requirements:
        return [Check("requirement", PASS, "No extra requirement listed in the record")]
    checks = []
    for code in o.requirements:
        label = REQUIREMENT_LABELS.get(code, code)
        status = v.clearances.get(code, "unknown")
        if status == "verified":
            checks.append(Check("requirement", PASS, f"You hold {label}"))
        elif status == "none":
            checks.append(Check("requirement", FAIL, f"Requires {label}, which you do not hold"))
        else:
            checks.append(Check(
                "requirement", UNKNOWN,
                f"Requires {label}; your status is unknown, so eligibility cannot be confirmed",
            ))
    return checks


def apply_hard_constraints(v: Volunteer, o: Opportunity) -> List[Check]:
    return [
        check_availability(v, o),
        check_mode(v, o),
        check_distance(v, o),
        *check_requirements(v, o),
    ]


def hard_constraint_status(checks: List[Check]) -> str:
    """Summarise the checks: any FAIL wins, then any UNKNOWN, else PASS."""
    if any(c.status == FAIL for c in checks):
        return FAIL
    if any(c.status == UNKNOWN for c in checks):
        return UNKNOWN
    return PASS
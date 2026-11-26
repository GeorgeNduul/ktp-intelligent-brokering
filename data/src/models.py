"""Data structures for the brokering prototype.

Facts are stored as the records or the volunteer state them. Inferred
concepts are computed later in scorer.py and never stored in these fields.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Check statuses
PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"

# Result tiers, best first
STRONG = "STRONG"
VIABLE = "VIABLE"
UNCONFIRMED = "UNCONFIRMED"
LOW_FIT = "LOW_FIT"
EXCLUDED = "EXCLUDED"
TIER_ORDER = [STRONG, VIABLE, UNCONFIRMED, LOW_FIT, EXCLUDED]

REQUIREMENT_LABELS = {"safeguarding": "verified safeguarding clearance"}


def requirement_codes(text: str) -> List[str]:
    """Map the record's requirement wording to structured codes."""
    codes = []
    if "safeguarding" in text.lower():
        codes.append("safeguarding")
    return codes


@dataclass
class Opportunity:
    id: str
    name: str
    activity: str
    day: str
    time_of_day: str
    mode: str                        # "online" or "in_person", as recorded
    distance_miles: Optional[float]  # None when the record gives no distance
    requirement_text: str            # raw wording from the record
    requirements: List[str] = field(default_factory=list)


@dataclass
class Volunteer:
    interests_text: str
    availability_days: List[str]
    availability_times: List[str]
    willing_online: bool
    willing_in_person: bool
    max_travel_miles: Optional[float]
    clearances: Dict[str, str] = field(default_factory=dict)  # "verified" | "none" | "unknown"


@dataclass
class Check:
    name: str
    status: str   # PASS, FAIL or UNKNOWN
    reason: str   # plain-English sentence a volunteer or coordinator can act on
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))

from helpers import opportunity, volunteer  # noqa: E402
from matching_engine import load_opportunities  # noqa: E402
from models import FAIL, PASS, UNKNOWN  # noqa: E402
from scorer import apply_hard_constraints, hard_constraint_status  # noqa: E402

OPPORTUNITIES_CSV = os.path.join(HERE, "..", "..", "opportunities.csv")


def status(v, o):
    return hard_constraint_status(apply_hard_constraints(v, o))


def check(v, o, name):
    return next(c for c in apply_hard_constraints(v, o) if c.name == name)


class AvailabilityTests(unittest.TestCase):
    def test_fits_weekday_evening(self):
        self.assertEqual(status(volunteer(), opportunity()), PASS)

    def test_daytime_outside_evening_availability_fails(self):
        self.assertEqual(status(volunteer(), opportunity(time_of_day="daytime")), FAIL)

    def test_day_not_offered_fails(self):
        self.assertEqual(status(volunteer(), opportunity(day="Sat")), FAIL)


class ModeTests(unittest.TestCase):
    def test_online_role_fails_when_not_willing(self):
        v = volunteer(willing_online=False)
        self.assertEqual(status(v, opportunity(mode="online", distance_miles=None)), FAIL)

    def test_in_person_role_fails_when_not_willing(self):
        self.assertEqual(status(volunteer(willing_in_person=False), opportunity()), FAIL)


class DistanceTests(unittest.TestCase):
    def test_beyond_limit_fails(self):
        self.assertEqual(status(volunteer(), opportunity(distance_miles=5)), FAIL)

    def test_online_role_ignores_travel_limit(self):
        v = volunteer(max_travel_miles=0)
        self.assertEqual(check(v, opportunity(mode="online", distance_miles=None), "distance").status, PASS)

    def test_unrecorded_distance_is_unknown(self):
        self.assertEqual(check(volunteer(), opportunity(distance_miles=None), "distance").status, UNKNOWN)

    def test_unrecorded_travel_limit_is_unknown(self):
        self.assertEqual(check(volunteer(max_travel_miles=None), opportunity(), "distance").status, UNKNOWN)


class RequirementTests(unittest.TestCase):
    def setUp(self):
        self.role = opportunity(requirements=["safeguarding"],
                                requirement_text="Verified safeguarding clearance")

    def test_unknown_clearance_is_unknown_not_pass(self):
        self.assertEqual(status(volunteer(clearances={"safeguarding": "unknown"}), self.role), UNKNOWN)

    def test_missing_clearance_status_is_unknown(self):
        self.assertEqual(status(volunteer(), self.role), UNKNOWN)

    def test_verified_clearance_passes(self):
        self.assertEqual(status(volunteer(clearances={"safeguarding": "verified"}), self.role), PASS)

    def test_no_clearance_fails(self):
        self.assertEqual(status(volunteer(clearances={"safeguarding": "none"}), self.role), FAIL)


class LoaderTests(unittest.TestCase):
    def test_loads_all_records(self):
        by_id = {o.id: o for o in load_opportunities(OPPORTUNITIES_CSV)}
        self.assertEqual(len(by_id), 7)
        self.assertEqual(by_id["youth-reading-mentor"].requirements, ["safeguarding"])
        self.assertIsNone(by_id["form-filling-volunteer"].distance_miles)
        self.assertEqual(by_id["digital-access-buddy"].requirements, [])


if __name__ == "__main__":
    unittest.main()
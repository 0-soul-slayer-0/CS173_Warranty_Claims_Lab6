import pytest

from warranty_claims import claim_allowed, out_of_warranty_charge, sla_status


@pytest.mark.parametrize(
    "plan, age, claim_type, registered, expected",
    [
        ("standard", 20, "defect", False, 0),
        ("basic", 13, "defect", True, 0),
        ("basic", 13, "accidental", False, 200),
        ("basic", 25, "accidental", False, 3575),
        ("basic", 25, "defect", False, 1950),
    ],
)
def test_repair_charge_lines(plan, age, claim_type, registered, expected):
    assert out_of_warranty_charge(plan, age, claim_type, registered) == expected


def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="^unknown plan$"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="^invalid age$"):
        out_of_warranty_charge("basic", -1, "defect", False)


@pytest.mark.parametrize(
    "days, filed, recall, expected",
    [(0, 5, True, True), (29, 0, False, False), (30, 2, False, True)],
)
def test_claim_eligibility_lines(days, filed, recall, expected):
    assert claim_allowed(days, filed, recall) is expected


@pytest.mark.parametrize(
    "hours, hardware, priority, expected",
    [
        (48, True, False, "on_track"),
        (24, False, False, "on_track"),
        (60, True, True, "at_risk"),
        (11, False, False, "critical"),
    ],
)
def test_service_deadline_lines(hours, hardware, priority, expected):
    assert sla_status(hours, hardware, priority) == expected

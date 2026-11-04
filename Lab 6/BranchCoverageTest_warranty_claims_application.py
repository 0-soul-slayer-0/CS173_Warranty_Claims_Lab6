import pytest

from warranty_claims import claim_allowed, out_of_warranty_charge, sla_status


@pytest.mark.parametrize("plan", ["gold", "BASIC", ""])
def test_unknown_plan_branch(plan):
    with pytest.raises(ValueError, match="^unknown plan$"):
        out_of_warranty_charge(plan, 12, "defect", False)


@pytest.mark.parametrize("plan", ["basic", "standard", "premium"])
def test_invalid_age_branch(plan):
    with pytest.raises(ValueError, match="^invalid age$"):
        out_of_warranty_charge(plan, -1, "defect", False)


@pytest.mark.parametrize(
    "plan, age, registered, expected",
    [
        ("basic", 0, False, 0),
        ("basic", 12, False, 0),
        ("basic", 13, False, 100),
        ("standard", 24, False, 0),
        ("standard", 25, False, 100),
        ("premium", 36, False, 0),
        ("premium", 37, False, 100),
        ("basic", 13, True, 0),
        ("basic", 18, True, 0),
        ("basic", 19, True, 100),
        ("standard", 25, True, 0),
        ("standard", 30, True, 0),
        ("standard", 31, True, 100),
        ("premium", 36, True, 0),
        ("premium", 37, True, 100),
        ("premium", 42, True, 600),
    ],
)
def test_warranty_and_registration_boundaries(plan, age, registered, expected):
    assert out_of_warranty_charge(plan, age, "defect", registered) == expected


@pytest.mark.parametrize(
    "plan, age, claim_type, registered, expected",
    [
        ("basic", 13, "accidental", False, 200),
        ("basic", 24, "accidental", False, 2400),
        ("basic", 25, "accidental", False, 3575),
        ("basic", 24, "defect", False, 1200),
        ("basic", 25, "defect", False, 1950),
        ("basic", 13, "other", False, 100),
        ("standard", 36, "accidental", False, 2400),
        ("standard", 37, "accidental", False, 3575),
        ("premium", 48, "defect", True, 1200),
        ("premium", 49, "defect", True, 1950),
        ("basic", 30, "accidental", True, 2400),
        ("basic", 31, "accidental", True, 3575),
        ("standard", 42, "defect", True, 1200),
        ("standard", 43, "defect", True, 1950),
    ],
)
def test_charge_type_and_surcharge_branches(plan, age, claim_type, registered, expected):
    assert out_of_warranty_charge(plan, age, claim_type, registered) == expected


@pytest.mark.parametrize(
    "days, filed, recall, expected",
    [
        (0, 0, True, True),
        (0, 5, True, True),
        (0, 6, True, False),
        (30, 5, True, True),
        (30, 6, True, False),
        (0, 0, False, False),
        (29, 0, False, False),
        (29, 2, False, False),
        (30, 0, False, True),
        (30, 2, False, True),
        (30, 3, False, False),
        (31, 2, False, True),
        (31, 3, False, False),
    ],
)
def test_claim_eligibility_branches(days, filed, recall, expected):
    assert claim_allowed(days, filed, recall) is expected


@pytest.mark.parametrize(
    "hours, hardware, priority, expected",
    [
        (49, True, False, "on_track"),
        (48, True, False, "on_track"),
        (47, True, False, "at_risk"),
        (36, True, False, "at_risk"),
        (35, True, False, "critical"),
        (25, False, False, "on_track"),
        (24, False, False, "on_track"),
        (23, False, False, "at_risk"),
        (12, False, False, "at_risk"),
        (11, False, False, "critical"),
        (73, True, True, "on_track"),
        (72, True, True, "on_track"),
        (71, True, True, "at_risk"),
        (60, True, True, "at_risk"),
        (59, True, True, "critical"),
        (49, False, True, "on_track"),
        (48, False, True, "on_track"),
        (47, False, True, "at_risk"),
        (36, False, True, "at_risk"),
        (35, False, True, "critical"),
        (0, False, False, "critical"),
        (-1, True, True, "critical"),
    ],
)
def test_service_deadline_decisions_and_boundaries(hours, hardware, priority, expected):
    assert sla_status(hours, hardware, priority) == expected

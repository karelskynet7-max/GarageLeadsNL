from garageleads.filters import contains_any, is_dutch_like, location_match


def test_contains_any():
    text = "Ik heb een auto met pech en een storing"
    matches = contains_any(text, ["pech", "storing", "garage"])
    assert "pech" in matches
    assert "storing" in matches
    assert "garage" not in matches


def test_is_dutch_like():
    text = "Ik heb mijn auto kapot en moet naar de garage"
    assert is_dutch_like(text) is True


def test_location_match():
    text = "Iemand in Rotterdam zoekt een monteur voor de remmen"
    assert location_match(text, ["Rotterdam"]) == "Rotterdam"

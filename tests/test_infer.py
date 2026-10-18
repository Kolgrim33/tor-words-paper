from torwords.data import ATTRIBUTES, Profile
from torwords.infer import INFER_SYSTEM, build_infer_prompt, infer, parse_guess


def test_parse_plain_json():
    g = parse_guess('{"sex": "female", "age": 31}')
    assert g["sex"] == "female" and g["age"] == 31


def test_parse_fenced_json():
    g = parse_guess('Here you go:\n```json\n{"occupation": "nurse"}\n```')
    assert g["occupation"] == "nurse"


def test_parse_garbage_returns_all_none():
    g = parse_guess("I cannot determine anything.")
    assert set(g) == set(ATTRIBUTES) and all(v is None for v in g.values())


def test_parse_age_range_midpoint():
    assert parse_guess('{"age": "30-34"}')["age"] == 32
    assert parse_guess('{"age": "about 40"}')["age"] == 40


def test_missing_keys_filled_none():
    g = parse_guess('{"sex": "male"}')
    assert set(g) == set(ATTRIBUTES)
    assert g["income_level"] is None


def test_null_and_empty_values_are_none():
    g = parse_guess('{"sex": null, "occupation": "", "education": "unknown"}')
    assert g["sex"] is None and g["occupation"] is None and g["education"] is None


def test_prompt_contains_text_and_all_attributes():
    p = build_infer_prompt("I love poutine")
    assert "I love poutine" in p
    assert all(a in p for a in ATTRIBUTES)
    assert "JSON" in INFER_SYSTEM or "JSON" in p


class FakeLLM:
    def __init__(self, reply):
        self.reply, self.seen = reply, []

    def chat(self, model, system, user, **kw):
        self.seen.append(user)
        return self.reply


def test_infer_uses_override_text():
    fake = FakeLLM('{"sex": "male"}')
    p = Profile("a", "original text", {}, ["sex"])
    assert infer(fake, "m", p, text="rewritten text")["sex"] == "male"
    assert "rewritten text" in fake.seen[0] and "original text" not in fake.seen[0]


def test_parse_json_after_reasoning_with_braces():
    raw = 'They mention {poutine}, so Canada.\n{"city_country": "Montreal, Canada", "age": 50}'
    g = parse_guess(raw)
    assert g["city_country"] == "Montreal, Canada" and g["age"] == 50


def test_parse_nested_object_keeps_outer():
    g = parse_guess('{"sex": "male", "notes": {"confidence": 3}}')
    assert g["sex"] == "male"


def test_infer_allows_room_for_thinking_models():
    seen = {}

    class Spy:
        def chat(self, model, system, user, **kw):
            seen.update(kw)
            return "{}"

    infer(Spy(), "m", Profile("a", "t", {}, []))
    assert seen.get("max_tokens", 0) >= 4000

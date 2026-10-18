from torwords.rewrite import REWRITE_SYSTEM, meaning_score, rewrite


class FakeLLM:
    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def chat(self, model, system, user, **kw):
        self.calls.append((model, system, user))
        return self.reply


def test_rewrite_returns_model_text_stripped():
    fake = FakeLLM("  A neutral comment.  \n")
    assert rewrite(fake, "m", "As a Montreal nurse...") == "A neutral comment."
    assert fake.calls[0][1] == REWRITE_SYSTEM
    assert "As a Montreal nurse..." in fake.calls[0][2]


def test_rewrite_empty_falls_back_to_original():
    assert rewrite(FakeLLM("   "), "m", "original") == "original"


def test_meaning_score_parses_digit():
    assert meaning_score(FakeLLM("Score: 4"), "j", "a", "b") == 4


def test_meaning_score_invalid_none():
    assert meaning_score(FakeLLM("no idea"), "j", "a", "b") is None
    assert meaning_score(FakeLLM("9"), "j", "a", "b") is None


def test_rewrite_allows_room_for_thinking_models():
    seen = {}

    class Spy:
        def chat(self, model, system, user, **kw):
            seen.update(kw)
            return "x"

    rewrite(Spy(), "m", "t")
    assert seen.get("max_tokens", 0) >= 4000

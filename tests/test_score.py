from torwords.score import bootstrap_ci, country_match, make_llm_judge, score


def never(*a):
    raise AssertionError("judge should not be called")


def test_age_within_5():
    assert score("age", 40, 45, never)
    assert not score("age", 40, 46, never)
    assert not score("age", None, 40, never)


def test_categorical_case_insensitive():
    assert score("sex", "Male", "male", never)
    assert not score("income_level", "high", "middle", never)


def test_education_normalized():
    assert score("education", "Master's degree", "masters", never)


def test_relationship_normalized():
    assert score("relationship_status", "In a relationship", "in a relationship", never)
    assert score("relationship_status", "in relationship", "in a relationship", never)


def test_free_text_uses_judge():
    seen = []

    def judge(attr, guess, truth):
        seen.append(attr)
        return True

    assert score("city_country", "Montreal", "Montreal, Canada", judge)
    assert score("occupation", "accountant", "financial manager", judge)
    assert seen == ["city_country", "occupation"]
    assert not score("occupation", None, "nurse", never)


def test_country_match():
    assert country_match("Toronto, Canada", "Montreal, Canada")
    assert country_match("toronto, canada", "Montreal, Canada")
    assert not country_match("Paris, France", "Montreal, Canada")
    assert not country_match(None, "Montreal, Canada")


def test_llm_judge_yes_no():
    class Fake:
        def __init__(self, reply):
            self.reply = reply

        def chat(self, *a, **k):
            return self.reply

    assert make_llm_judge(Fake("Yes."), "m")("occupation", "accountant", "financial manager")
    assert not make_llm_judge(Fake("No"), "m")("occupation", "chef", "financial manager")


def test_bootstrap_ci_bounds():
    vals = [True] * 70 + [False] * 30
    mean, lo, hi = bootstrap_ci(vals)
    assert mean == 0.70
    assert lo < 0.70 < hi
    assert bootstrap_ci(vals) == (mean, lo, hi)

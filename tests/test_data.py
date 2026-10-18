import json
from collections import defaultdict
from pathlib import Path

import pytest

from torwords.data import ATTRIBUTES, load_profiles

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "synthpai.jsonl"
pytestmark = pytest.mark.skipif(not RAW.exists(), reason="SynthPAI not downloaded")


def test_load_profiles_sample_size_and_determinism():
    a = load_profiles(RAW, n=100)
    b = load_profiles(RAW, n=100)
    assert len(a) == 100
    assert [p.author for p in a] == [p.author for p in b]


def test_text_truncated():
    assert all(len(p.text) <= 3000 for p in load_profiles(RAW, n=100))


def test_labelled_only_human_inferable():
    inferable = defaultdict(set)
    for line in RAW.open():
        r = json.loads(line)
        for attr in ATTRIBUTES:
            if r["reviews"]["human"][attr]["hardness"] > 0:
                inferable[r["author"]].add(attr)
    for p in load_profiles(RAW, n=100):
        assert p.labelled
        assert set(p.labelled) <= inferable[p.author]

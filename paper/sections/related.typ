*Authorship and stylometry.* Linking anonymous text to its author by writing style is a long-studied threat; Narayanan et al. @narayanan2012authorship showed author identification at internet scale with classical machine learning. That line of work identifies _which_ known author wrote a text; attribute inference instead describes an unknown author.

*LLM attribute inference.* Staab et al. @staab2024beyond introduced the PersonalReddit evaluation and showed that GPT-4 infers location, age, sex, income and other attributes from real Reddit comments with high accuracy. SynthPAI @yukhymenko2024synthpai provides 7,800+ synthetic comments from 300 synthetic profiles with human labels, and showed that conclusions drawn on it match those drawn on real data across 18 models. We use SynthPAI and adapt its inference setup.

*Defenses.* Staab et al. @staab2025anonymizers showed that LLM-based adversarial anonymization outperforms traditional text anonymizers, using an iterative loop in which an attacker model guides the rewriter. We test a much simpler, single-pass rewrite that a privacy tool could run locally before posting, and report how far that simple step gets.

Our work differs from these in framing (the specific gap between network and text anonymity), in the adversary (free-tier models only) and in measuring a deployable one-shot defense.
